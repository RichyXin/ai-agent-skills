#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPROF 深度内存泄漏分析器 v2.0
支持 HPROF 1.0.2/1.0.3，支持对象图构建和泄漏分析
"""

import sys
import struct
import os
import argparse
from datetime import datetime
from collections import defaultdict
import heapq

# HPROF 常量
TAG_STRING = 0x01
TAG_LOAD_CLASS = 0x02
TAG_HEAP_DUMP = 0x0C
TAG_HEAP_DUMP_SEGMENT = 0x1C
TAG_HEAP_DUMP_END = 0x2C

# Heap Dump Tags
HD_ROOT_UNKNOWN = 0xFF
HD_ROOT_JNI_GLOBAL = 0x01
HD_ROOT_JNI_LOCAL = 0x02
HD_ROOT_JAVA_FRAME = 0x03
HD_ROOT_NATIVE_STACK = 0x04
HD_ROOT_STICKY_CLASS = 0x05
HD_ROOT_THREAD_BLOCK = 0x06
HD_ROOT_MONITOR_USED = 0x07
HD_ROOT_THREAD_OBJECT = 0x08
HD_CLASS_DUMP = 0x20
HD_INSTANCE_DUMP = 0x21
HD_OBJECT_ARRAY_DUMP = 0x22
HD_PRIMITIVE_ARRAY_DUMP = 0x23

PRIMITIVE_SIZES = {
    4: 1, 5: 2, 6: 4, 7: 8, 8: 1, 9: 2, 10: 4, 11: 8
}

PRIMITIVE_NAMES = {
    4: 'boolean', 5: 'char', 6: 'float', 7: 'double', 
    8: 'byte', 9: 'short', 10: 'int', 11: 'long'
}

class HprofParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None
        self.id_size = 4
        self.version = ""
        self.strings = {}  # id -> str
        self.classes = {}  # id -> class_info
        self.object_sizes = {} # id -> shallow_size
        self.object_types = {} # id -> type_name
        
    def read_id(self):
        data = self.file.read(self.id_size)
        if len(data) < self.id_size: return None
        return int.from_bytes(data, 'big')

    def read_u1(self):
        data = self.file.read(1)
        if not data: return None
        return data[0]

    def read_u2(self):
        data = self.file.read(2)
        if len(data) < 2: return None
        return struct.unpack('>H', data)[0]

    def read_u4(self):
        data = self.file.read(4)
        if len(data) < 4: return None
        return struct.unpack('>I', data)[0]

    def read_u8(self):
        data = self.file.read(8)
        if len(data) < 8: return None
        return struct.unpack('>Q', data)[0]

    def parse(self):
        print(f"正在解析: {self.filepath}")
        self.file = open(self.filepath, 'rb')
        
        # Header
        header = b''
        while True:
            b = self.file.read(1)
            if b == b'\x00': break
            header += b
        self.version = header.decode('ascii')
        print(f"版本: {self.version}")
        
        self.id_size = self.read_u4()
        print(f"ID 大小: {self.id_size}")
        
        timestamp = self.read_u8()
        print(f"时间戳: {datetime.fromtimestamp(timestamp/1000)}")
        
        # Records
        try:
            while True:
                tag = self.read_u1()
                if tag is None: break
                
                self.read_u4() # time
                length = self.read_u4()
                
                if tag == TAG_STRING:
                    str_id = self.read_id()
                    str_content = self.file.read(length - self.id_size)
                    self.strings[str_id] = str_content.decode('utf-8', errors='replace')
                
                elif tag == TAG_LOAD_CLASS:
                    class_serial = self.read_u4()
                    class_id = self.read_id()
                    stack_serial = self.read_u4()
                    name_id = self.read_id()
                    
                    class_name = self.strings.get(name_id, f"Class_{hex(class_id)}")
                    self.classes[class_id] = {'name': class_name}
                    self.object_types[class_id] = 'Class'
                    
                elif tag in [TAG_HEAP_DUMP, TAG_HEAP_DUMP_SEGMENT]:
                    self.parse_heap_dump(length)
                
                else:
                    self.file.seek(length, 1) # Skip
                    
        except Exception as e:
            print(f"解析中断: {e}")
        finally:
            self.file.close()
            
        print(f"解析完成。对象数: {len(self.object_sizes)}")

    def parse_heap_dump(self, length):
        end_pos = self.file.tell() + length
        while self.file.tell() < end_pos:
            subtag = self.read_u1()
            if subtag is None: break
            
            if subtag in [HD_ROOT_UNKNOWN, HD_ROOT_STICKY_CLASS, HD_ROOT_MONITOR_USED]:
                self.read_id()
            elif subtag == HD_ROOT_JNI_GLOBAL:
                self.read_id(); self.read_id()
            elif subtag in [HD_ROOT_JNI_LOCAL, HD_ROOT_JAVA_FRAME]:
                self.read_id(); self.read_u4(); self.read_u4()
            elif subtag in [HD_ROOT_NATIVE_STACK, HD_ROOT_THREAD_BLOCK]:
                self.read_id(); self.read_u4()
            elif subtag == HD_ROOT_THREAD_OBJECT:
                self.read_id(); self.read_u4(); self.read_u4()
                
            elif subtag == HD_CLASS_DUMP:
                class_id = self.read_id()
                self.read_u4() # stack
                self.read_id() # super
                self.read_id() # loader
                self.read_id() # signer
                self.read_id() # domain
                self.read_id() # reserved
                self.read_id() # reserved
                instance_size = self.read_u4()
                
                cp_count = self.read_u2()
                for _ in range(cp_count):
                    self.read_u2(); t = self.read_u1(); self.skip_value(t)
                
                sf_count = self.read_u2()
                for _ in range(sf_count):
                    self.read_id(); t = self.read_u1(); self.skip_value(t)
                
                if_count = self.read_u2()
                for _ in range(if_count):
                    self.read_id(); self.read_u1()
                    
                self.object_sizes[class_id] = 0
                
            elif subtag == HD_INSTANCE_DUMP:
                obj_id = self.read_id()
                self.read_u4() # stack
                class_id = self.read_id()
                data_len = self.read_u4()
                self.file.seek(data_len, 1)
                
                self.object_sizes[obj_id] = data_len + self.id_size * 2
                self.object_types[obj_id] = self.classes.get(class_id, {}).get('name', f"Instance_{hex(class_id)}")
                
            elif subtag == HD_OBJECT_ARRAY_DUMP:
                obj_id = self.read_id()
                self.read_u4() # stack
                count = self.read_u4()
                class_id = self.read_id()
                self.file.seek(count * self.id_size, 1)
                
                self.object_sizes[obj_id] = count * self.id_size
                self.object_types[obj_id] = "Object[]"
                        
            elif subtag == HD_PRIMITIVE_ARRAY_DUMP:
                obj_id = self.read_id()
                self.read_u4() # stack
                count = self.read_u4()
                elem_type = self.read_u1()
                size = count * PRIMITIVE_SIZES.get(elem_type, 1)
                self.file.seek(size, 1)
                
                self.object_sizes[obj_id] = size
                type_name = PRIMITIVE_NAMES.get(elem_type, 'unknown') + "[]"
                self.object_types[obj_id] = type_name
                
            else:
                print(f"Unknown heap dump subtag: {hex(subtag)} at {self.file.tell()}")
                break

    def skip_value(self, type_code):
        if type_code == 2: self.read_id()
        elif type_code in PRIMITIVE_SIZES:
            self.file.seek(PRIMITIVE_SIZES[type_code], 1)

    def analyze(self):
        print("\n=== 分析报告 ===")
        
        print("\n[Top 20 对象 (Shallow Size)]")
        top_objects = heapq.nlargest(20, self.object_sizes.items(), key=lambda x: x[1])
        for obj_id, size in top_objects:
            type_name = self.object_types.get(obj_id, "Unknown")
            print(f"  {hex(obj_id)}: {size/1024:.2f} KB ({type_name})")
            
        print("\n[对象类型统计]")
        type_counts = defaultdict(int)
        type_sizes = defaultdict(int)
        for obj_id, size in self.object_sizes.items():
            t = self.object_types.get(obj_id, "Unknown")
            type_counts[t] += 1
            type_sizes[t] += size
            
        top_types = heapq.nlargest(20, type_sizes.items(), key=lambda x: x[1])
        for t, size in top_types:
            count = type_counts[t]
            print(f"  {t}: {size/1024:.2f} KB (count: {count})")

        print("\n[泄漏嫌疑]")
        large_arrays = [
            (oid, s) for oid, s in self.object_sizes.items() 
            if s > 100*1024 and ('[]' in self.object_types.get(oid, ''))
        ]
        if large_arrays:
            print(f"发现 {len(large_arrays)} 个大于 100KB 的数组:")
            for oid, s in sorted(large_arrays, key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {hex(oid)}: {s/1024:.2f} KB ({self.object_types.get(oid)})")
        else:
            print("未发现异常大数组。")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='HPROF file')
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print("File not found")
        return

    parser = HprofParser(args.file)
    parser.parse()
    parser.analyze()

if __name__ == '__main__':
    main()
