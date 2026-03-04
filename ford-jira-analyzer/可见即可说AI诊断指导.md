# 可见即可说（Visible Speech）问题诊断专家指南

本指南旨在为 AI 助手提供“可见即可说”功能的分析逻辑与日志判定标准。通过追踪 UINode 的生命周期，快速定位功能不响应、执行错误或识别失败的根源。

## 1. 核心链路与关键日志汇总

在分析问题前，请优先检索并匹配以下关键日志点：

### 关键日志参考表
| 阶段 | 关键日志关键字 | 说明 |
| :--- | :--- | :--- |
| **全局配置** | `setVosFeature: MEGA_CSCS_ENABLE` | 可见即可说全局开关状态 |
| **扫描决策** | `needScanEvent` | 判断当前页面/事件是否被扫描逻辑忽略 |
| **性能/时效** | `ScanNodes cost` | 记录页面节点扫描耗时 |
| **全量细节** | `mars-debug` | 可见即可说全量调试日志，包含扫描到的节点详情 |
| **上报阶段** | `update UINode size` | 客户端 Mars 模块准备上报的节点数量 |
| **上报通道** | `MegaVosKits updateUINodeInfo` | VosSDK 接收并向云端同步节点信息的入口 |
| **云端响应** | `onVisibleDialogueResult` | 云端成功命中可见指令并下发回调 |
| **离线/普通响应** | `onDialogueResult` | 未走可见逻辑，普通语音回调（用于判定是否跳过可见） |
| **指令执行** | `handleUINode` | 客户端接收指令后，开始执行节点匹配与点击 |

---

## 2. 诊断逻辑：判定问题分类

收到问题时，首先通过日志判定属于哪一类问题：

### A. 非执行类问题（云端未下发指令）
**判定依据：** 日志中出现 `onDialogueResult` 但未出现 `onVisibleDialogueResult`。
*   **排查方向：**
    1.  **开关检查：** 确认 `MEGA_CSCS_ENABLE` 为 true。
    2.  **页面扫描：** 检查 `needScanEvent` 是否导致页面被跳过，查看 `ScanNodes cost` 是否超时。
    3.  **节点是否存在：** 搜索 `mars-debug` 确认目标节点的 `subjects` (名词) 和 `operations` (动词) 是否正确生成。
    4.  **上报检查：** 确认 `update UINode size` 数量不为 0，且 `MegaVosKits updateUINodeInfo` 已触发。
    5.  **云端匹配：** 检查 `useCloudResponse` 关键字。若为 false 则走离线逻辑（不下发指令）；若为 true 则需在云端平台排查。

### B. 执行类问题（云端下发但执行失败）
**判定依据：** 日志中已出现 `onVisibleDialogueResult`，进入 `handleUINode` 流程。
*   **排查方向：**
    1.  **节点查找：** 确认 `getActionInfo` 是否返回 `ActionInfoData`。若显示 `do nothing with invalid actionInfo`，说明客户端根据云端下发的 ID + Name 无法在当前页面找到对应 View。
    2.  **软提示拦截：** 确认是否命中“软提”逻辑（控件已在目标状态）。
    3.  **滚动异常：** 检查 `scroll_forward/backward/left/right` 动作是否被正确触发。

---

## 3. 常见客户端配置错误（针对 AI 自动扫描）

当 `mars-debug` 中找不到目标节点时，AI 应指导用户检查以下配置：

1.  **无障碍屏蔽：** 检查 View 是否设置了 `android:importantForAccessibility="no"`。
2.  **点击事件缺失：** 非文本类控件必须设置 `onClickListener` 才能被识别为可点击节点。
3.  **控件状态：** `android:enabled="false"` 的控件会被扫描忽略。
4.  **ContentDescription 格式：** 必须符合 `assistName`, `subjects`, `operations` 的 JSON 或特定格式要求。

---

## 4. 节点（UINode）生成逻辑

AI 在分析逻辑时应理解 UINode 的三种生成方式：
*   **显式配置：** 通过 `android:contentDescription` 属性定义（支持泛化说法）。
*   **隐式文本：** 文本类控件自动根据 `text` 内容生成 `subjects`。
*   **列表模式：** `ListView` 或 `RecyclerView` 若声明为 `nodeType="list"`，会生成带层级关系的节点，支持“第几个”这种说法。

---

## 5. 调试工具指令

引导开发或测试使用以下命令进行实时排查：
*   **启动调试面板：** `adb shell am startservice com.mega.assist.vui/.debugger.DebugService`
    *   *功能：* 标记页面节点、查看节点属性、模拟云端指令执行。
*   **过滤全量日志：** `adb logcat | grep -E "mars-debug|update UINode size|onVisibleDialogueResult|handleUINode"`

---

## 6. 云端日志分析

若确定客户端已上报节点但无响应，建议通过以下步骤查询云端：
1.  **获取 VID：** 从 VosSDK 日志中提取 `vehicle_id`。
2.  **查询 ReqInfo：** 在 `vos-debug` 平台根据 `rid` 或 `VID` 查找请求。
3.  **对比上报参数：** 确认 `uiNodes` 字段中是否包含目标节点的配置。
