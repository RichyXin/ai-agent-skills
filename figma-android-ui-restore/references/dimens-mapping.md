# Dimens 规则：MontereyMap vs CardiffMap

## 适用范围
- MontereyMap 模块：`monterey/MontereyMap/**`
- CardiffMap / CardiffMultiMap 模块：`cardiff/CardiffMap/**`、`cardiff/CardiffMultiMap/**`

## MontereyMap（mon_xx / mon_sp_xx）
- **所有尺寸**必须使用 `@dimen/mon_xx` 或 `R.dimen.mon_xx`。
- **所有字号**必须使用 `@dimen/mon_sp_xx` 或 `R.dimen.mon_sp_xx`。
- 禁止直接使用设计稿数值或 dp/sp 硬编码。
- dimen 定义：`cardiff/libs/CommonUtils/res/values/dimens_monterey.xml`
- 换算比例：**设计稿值 × 0.75 = 实际值**（由 mon_xx/mon_sp_xx 资源完成）。
- 注释禁止包含 Figma 数值。

示例：
```xml
android:layout_width="@dimen/mon_192"
android:layout_height="@dimen/mon_80"
android:textSize="@dimen/mon_sp_24"
```

## CardiffMap / CardiffMultiMap（common_xxdp / common_xxsp）
- **所有尺寸**必须使用 `@dimen/common_xxdp` 或 `R.dimen.common_xxdp`。
- **所有字号**必须使用 `@dimen/common_xxsp` 或 `R.dimen.common_xxsp`。
- 禁止硬编码数值或 dp/sp 直接计算。
- dimen 定义：`cardiff/libs/CommonUtils/res/values/dimens_common.xml`
- 资源范围完整，直接使用即可。

示例：
```xml
android:layout_width="@dimen/common_192dp"
android:layout_height="@dimen/common_80dp"
android:textSize="@dimen/common_24sp"
```

## 语义化尺寸（Cardiff）
如需语义化名称，在模块 `res/values/dimens.xml` 中引用 common 资源：
```xml
<dimen name="map_center_x_one_third">@dimen/common_260dp</dimen>
```
