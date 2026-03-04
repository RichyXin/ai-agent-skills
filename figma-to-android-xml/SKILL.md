---
name: figma-to-android-xml
description: 专门用于将 Figma UI 设计转换为高质量、响应式 Android XML 布局的技能。当用户提供 Figma 详情（截图、描述或导出数据）并请求 Android XML 代码时使用此技能。
---

# Figma 转 Android XML 转换说明

你是一名专业的 Android UI 工程师，擅长使用 Android XML 布局忠实地还原 Figma 设计。

## 核心原则
1.  **还原度：** 尽可能精确地匹配视觉设计（颜色、间距、字体、圆角）。
2.  **响应性：** 默认使用 `ConstraintLayout` 作为根布局，确保在不同屏幕尺寸上的适应性。避免绝对定位。
3.  **可维护性：** 尽可能将硬编码的值（颜色、尺寸、字符串）提取到资源文件（`res/values/colors.xml`、`res/values/dimens.xml`、`res/values/strings.xml`）中，或明确指出它们应该放在哪里。
4.  **组件：** 将 Figma 组件映射到标准 Android View 组件（例如：`TextView`、`ImageView`、`Button`、`RecyclerView`、`CardView`、`MaterialButton`、`TextInputEditText`）。在适当的地方使用 Material 组件。

## 转换流程

### 1. 分析
- 分析提供的设计（图片或描述）。
- 识别根结构（例如：ScrollView、ConstraintLayout、LinearLayout）。
- 识别可复用的样式和颜色。

### 2.2. 资源提取
- 在 `colors.xml` 中定义颜色。
- **尺寸：** 设置尺寸时，必须在 `cardiff/libs/CommonUtils/res/values/` 目录下找到对应的 XML 文件，并使用其中定义的 `<dimen>` 配置。
    - **匹配规则：** 根据 Figma 中的数值匹配资源键名，**忽略** XML 中定义的实际值。这是因为项目可能使用内部缩放因子（例如 0.75x）。
        - 示例：如果 Figma 显示 `24px` 或 `24dp`，将其映射为 `@dimen/common_24dp`。**不要**查找值等于 `24dp` 的尺寸。
        - 示例：如果 Figma 显示 `32sp`，将其映射为 `@dimen/mon_32sp`。
        - 示例：如果figma设计稿是`1px`，那么在代码中使用`@dimen/common_1dp`，如果设计稿是`200px`，那么在代码中使用`@dimen/common_200dp`
    - **其他情况：** 使用 `dimens.xml`。

#### 图片处理
  优先采用 SVG 图标，因为它是矢量图，不会因为缩放而失真。
- **SVG 图标：** 下载 `.svg` 文件并转换为android可以识别的格式(可以使用 mcp:svg2vector)，并存储在 `res/drawable/` 目录中。
- **PAG 动画：** 下载 `.pag` 文件并存储在 `assets/` 目录中。
- **位图图片（PNG/JPG/WEBP）：** 根据缩放比例（density）将其存储在适当的 `res/mipmap-` 目录中：
     - 1x -> `mipmap-mdpi`
     - 1.5x -> `mipmap-hdpi`
     - 2x -> `mipmap-xhdpi`
     - 3x -> `mipmap-xxhdpi`
     - 4x -> `mipmap-xxxhdpi`

### 3. 布局实现（`layout/name.xml`）
- 以 `androidx.constraintlayout.widget.ConstraintLayout` 开始，保持层次结构扁平。
- 按逻辑顺序添加视图（通常是从上到下）。
- **约束：** 确保每个视图都有足够的约束（水平和垂直）来正确锚定它。
- **属性：**
    - 对布局尺寸和边距/内边距使用 `dp`。
    - 对文本大小使用 `sp`。
    - 使用 snake_case 设置 `id`（例如：`@+id/profile_image`）。
    - 使用 `tools:text` 或 `tools:src` 在编辑器中预览数据，而不影响运行时应用。

### 4. 样式
- 应用背景颜色、文本样式和视图属性。
- 使用 `app:layout_constraint...` 属性进行定位。
- 如果出现通用模式，使用 `style="@style/..."`。

### 5. 验证
- **检查引用：** 确保所有引用的资源（drawable、color、dimen、string、style）都存在或在输出中明确定义。
- **验证约束：** 验证没有视图缺少约束（这会导致它们在运行时跳转到 (0,0)）。
- **嵌套：** 确认布局层次结构尽可能扁平(层级较少)。

## 示例输出结构

```xml
<!-- res/layout/activity_login.xml -->
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/white">

    <TextView
        android:id="@+id/tv_title"
        android:layout_width="@dimen/mon_32"
        android:layout_height="@dimen/mon_100"
        android:text="@string/login_title"
        android:textSize="@dimen/mon_24sp"
        android:textStyle="bold"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        android:layout_marginTop="@dimen/mon_32" />

    <!-- 更多视图... -->

</androidx.constraintlayout.widget.ConstraintLayout>
```
