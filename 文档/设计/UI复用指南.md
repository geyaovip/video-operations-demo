# UI复用指南

版本：2026-10-19。与[界面与交互规范](界面与交互.md)配套，供新项目接入同一套视觉和交互。此处提供起步样式和实施模板，不是完整组件库；菜单、弹窗、选择、保存和路由仍需接入目标项目的真实逻辑。

## 1. 新项目拿哪些内容

| 内容 | 是否复用 | 接入方式 |
| --- | --- | --- |
| 通用规范本文及界面与交互规范 | 是 | 放入目标项目的设计文档目录，建立唯一入口 |
| 颜色、字号、间距、圆角、按钮规格 | 是 | 映射到目标工程Token／主题，不复制重复CSS覆盖 |
| 字段、状态、分页、返回、离开保护等交互契约 | 是 | 在项目组件与路由中实现，同一行为共用控制器 |
| 页面模板 | 按需要 | 选择列表、详情、编辑、工作区等，不必全部具备 |
| 视频运营项目规则 | 否，作参考 | 用新项目自己的业务适配表替换 |
| 单HTML、Hash、本地存储、制作队列 | 否 | 由目标项目工程和服务架构决定 |
| 企业名、素材、平台Logo、样本记录 | 否 | 使用新项目正式资产及合法数据 |
| 当前任务演示动画、未接入适配器 | 否 | 真实状态来自目标项目服务，不复制预置循环进度 |

不需要将视频运营全部目录复制进新项目，也不需要照搬9MB的HTML。视觉复用不要求复制业务代码、历史迁移或媒体文件。

## 2. 接入顺序

1. **确定项目配置。** 填写第3节：品牌、入口、资源、权限、业务状态、保存能力和真实服务边界。
2. **映射基础变量。** 保留语义名，先检查主色、文字、表面和状态色，再接字体、间距和尺寸。
3. **实现基础组件。** 按钮、表单项、输入、选择、标签、提示、卡片、分页、弹窗；每个组件包含状态和键盘行为。
4. **实现公共交互。** 查询暂存／应用、分页恢复、逻辑返回、未保存保护、待选集合、异步防重与过期结果检查。
5. **做三类代表页面。** 一个列表、一个详情／编辑、一个弹窗或工作区，核对PC和手机，再扩展其余模块。
6. **接真实业务。** 保存、上传、生成、发送和同步分别定义成功条件，不用Toast或动画替代实际结果。
7. **补全异常并验收。** 加测权限不足、空态、错误、冲突、重复点击、断网、返回恢复、输入法和临界断点。

采用已有组件库时优先改主题和封装公共行为。不要另写一套相同按钮，又在页面用不同组件库的弹窗和选择器，导致焦点、字号和操作高度不一致。

## 3. 项目适配模板

将下表复制到目标项目自身的UI规则中，填具体值；不要只写“与视频运营一致”。

| 项目项 | 必填约定 |
| --- | --- |
| 产品范围 | 当前主要任务、主要资源、不包含哪些业务阶段 |
| 品牌与资产 | 产品名、Logo、平台图标、主色是否替换、许可来源 |
| 应用框架 | PC侧栏／顶栏、手机导航、收窄逻辑、默认入口 |
| 工作范围 | 租户／空间／门店等范围定义、切换前输入保护、数据隔离 |
| 列表 | 核心列、卡片字段、查询何时应用、默认排序、分页、空态 |
| 资源层级 | 每种详情与编辑的父级；跨模块跳转如何返回 |
| 业务状态 | 原始状态→展示状态→颜色→可执行操作，未知结果单独定义 |
| 表单保存 | 哪些可保存草稿、哪些只能完整提交、保存后去向 |
| 删除与取消 | 是否可恢复、引用限制、取消窗口是否终止任务 |
| 异步任务 | 排队／执行／完成／失败／未知结果，关页与断网的后果 |
| 上传与下载 | 格式／大小／数量、入库与采用、取消后保留、文件版本 |
| 权限 | 查看、编辑、执行与管理权限；无权操作的展示和提交校验 |
| AI辅助 | 默认上下文、建议采用、工作单保存、历史恢复、真实模型边界 |
| 响应式例外 | 组件断点、双栏转分级、固定操作、安全区和键盘 |
| 实现例外 | 每项偏离通用规范的理由、范围及验收方式 |

“审批／审核是否存在”“生成后能否编辑”“是否允许取消任务”等由目标项目明确，不继承视频运营的产品取舍。

## 4. 可复制的基础变量与起步样式

以下使用`ui-`命名空间，避免与现有业务类冲突。数值来自当前浅色风格，间距变量和命名为复用整理；不是把原CSS逐行抽取出来。目标项目可映射到现有主题系统，不强制沿用类名。

CSS仅覆盖基本样式；loading锁、非法值检查、焦点陷阱、状态朗读、键盘选择和路由恢复需要控制器配合。代码不引用任何外部字体、图标或业务文件。

```css
.ui-kit {
  --ui-primary: #6554d9;
  --ui-primary-hover: #5543c4;
  --ui-primary-soft: #f0edff;
  --ui-bg: #f6f7fb;
  --ui-surface: #fff;
  --ui-neutral-soft: #f1f3f7;
  --ui-text: #202535;
  --ui-sub: #596174;
  --ui-hint: #687185;
  --ui-line: #e3e6ee;
  --ui-input-border: #a7afbd;
  --ui-success: #187b4d;
  --ui-warning: #956000;
  --ui-danger: #bf3434;
  --ui-info: #255cb5;
  --ui-success-soft: #edf8f1;
  --ui-warning-soft: #fff6df;
  --ui-danger-soft: #fff0f0;
  --ui-info-soft: #edf3ff;
  --ui-secondary: #f5f6fa;
  --ui-secondary-hover: #e9ecf3;
  --ui-button-border: #cfd4df;
  --ui-button-border-hover: #b6bece;
  --ui-disabled-bg: #f0f1f5;
  --ui-disabled-text: #9399a7;
  --ui-space-1: 4px;
  --ui-space-2: 8px;
  --ui-space-3: 12px;
  --ui-space-4: 16px;
  --ui-space-5: 20px;
  --ui-space-6: 24px;
  --ui-space-8: 32px;
  --ui-radius-control: 6px;
  --ui-radius-card: 10px;
  --ui-radius-dialog: 12px;
  --ui-control-height: 40px;
  --ui-hit-size: 40px;
  --ui-page-gutter: 32px;
  --ui-grid-gap: 20px;
  --ui-card-padding: 24px;
  --ui-transition: 150ms;
  font: 400 14px/1.7 -apple-system, BlinkMacSystemFont,
    "PingFang SC", "Microsoft YaHei", sans-serif;
  color: var(--ui-text);
}
.ui-kit, .ui-kit *, .ui-kit *::before, .ui-kit *::after {
  box-sizing: border-box;
}
.ui-kit .ui-card {
  min-width: 0;
  padding: var(--ui-card-padding);
  background: var(--ui-surface);
  border: 1px solid var(--ui-line);
  border-radius: var(--ui-radius-card);
}
.ui-kit .ui-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--ui-grid-gap);
}
.ui-kit .ui-section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
}
.ui-kit .ui-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: var(--ui-control-height);
  padding: 9px 14px;
  border: 1px solid var(--ui-button-border);
  border-radius: var(--ui-radius-control);
  background: var(--ui-secondary);
  color: var(--ui-sub);
  font: inherit;
  font-size: 13px;
  font-weight: 500;
  line-height: 20px;
  cursor: pointer;
  touch-action: manipulation;
  transition: background-color var(--ui-transition),
    color var(--ui-transition), border-color var(--ui-transition);
}
.ui-kit .ui-btn:hover:not(:disabled) {
  background: var(--ui-secondary-hover);
  border-color: var(--ui-button-border-hover);
}
.ui-kit .ui-btn--primary {
  background: var(--ui-primary);
  border-color: transparent;
  color: #fff;
}
.ui-kit .ui-btn--primary:hover:not(:disabled) {
  background: var(--ui-primary-hover);
  border-color: transparent;
}
.ui-kit .ui-btn--light, .ui-kit .ui-btn--icon {
  background: transparent;
  border-color: transparent;
  color: var(--ui-primary);
}
.ui-kit .ui-btn--light:hover:not(:disabled),
.ui-kit .ui-btn--icon:hover:not(:disabled) {
  background: var(--ui-primary-soft);
  border-color: transparent;
}
.ui-kit .ui-btn--icon {
  width: var(--ui-hit-size);
  min-width: var(--ui-hit-size);
  height: var(--ui-hit-size);
  padding: 10px;
  color: var(--ui-sub);
}
.ui-kit .ui-btn--danger {
  background: #fff7f7;
  border-color: #e9bfc1;
  color: var(--ui-danger);
}
.ui-kit .ui-btn--danger:hover:not(:disabled) {
  background: var(--ui-danger-soft);
  border-color: #e9bfc1;
}
.ui-kit .ui-btn--danger-solid {
  background: var(--ui-danger);
  border-color: transparent;
  color: #fff;
}
.ui-kit .ui-btn--danger-solid:hover:not(:disabled) {
  background: #b52c32;
  border-color: transparent;
}
.ui-kit .ui-btn:active:not(:disabled) { filter: brightness(.96); }
.ui-kit .ui-btn:focus-visible {
  outline: 2px solid var(--ui-primary);
  outline-offset: 2px;
}
.ui-kit .ui-btn:disabled {
  background: var(--ui-disabled-bg);
  border-color: transparent;
  color: var(--ui-disabled-text);
  cursor: not-allowed;
}
.ui-kit .ui-field { display: grid; gap: 8px; min-width: 0; }
.ui-kit .ui-field > label { font-size: 13px; font-weight: 500; }
.ui-kit .ui-input {
  width: 100%;
  min-width: 0;
  min-height: var(--ui-control-height);
  padding: 9px 12px;
  border: 1px solid var(--ui-input-border);
  border-radius: var(--ui-radius-control);
  background: var(--ui-surface);
  color: var(--ui-text);
  font: inherit;
  line-height: 20px;
}
.ui-kit textarea.ui-input { resize: vertical; line-height: 1.7; }
.ui-kit .ui-input:focus {
  outline: 1px solid var(--ui-primary);
  outline-offset: -1px;
  border-color: var(--ui-primary);
}
.ui-kit .ui-input[aria-invalid="true"] {
  border-color: var(--ui-danger);
}
.ui-kit .ui-field-message { font-size: 12px; line-height: 18px; }
.ui-kit .ui-field-message--error { color: var(--ui-danger); }
.ui-kit .ui-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
@media (max-width: 1199px) and (min-width: 960px) {
  .ui-kit { --ui-page-gutter: 20px; }
}
@media (max-width: 767px) {
  .ui-kit {
    --ui-control-height: 44px;
    --ui-hit-size: 44px;
    --ui-page-gutter: 16px;
    --ui-grid-gap: 16px;
    --ui-card-padding: 18px 16px;
  }
  .ui-kit .ui-grid { grid-template-columns: minmax(0, 1fr); }
  .ui-kit .ui-input { font-size: 16px; line-height: 24px; }
  .ui-kit .ui-actions > .ui-btn { flex: 1; min-width: 0; }
  .ui-kit .ui-actions:has(> .ui-btn:nth-child(3)) {
    flex-direction: column;
  }
}
@media (max-width: 359px) {
  .ui-kit { --ui-page-gutter: 12px; }
}
@media (prefers-reduced-motion: reduce) {
  .ui-kit .ui-btn { transition: none; }
}
```

原生button通常有浏览器默认字体，因此示例先继承字体，再明确字号、字重和行高。接入后还应通过目标工程的CSS解析器及浏览器核对，不能仅凭代码块可复制就认定全部兼容。

`.ui-actions`仅包围当前一组底部操作；页头、筛选条和行内操作分别布局，不能把所有按钮都套入同一个等宽规则。使用Portal／Teleport渲染弹窗时，主题变量和作用域也需要挂在Portal根，避免浮层丢失主题。

## 5. 组件行为交接表

每实现一个组件，至少补齐下表；“已有样式”不能当作“组件已完成”。

| 组件 | 输入／配置 | 事件与状态 | 必须处理 |
| --- | --- | --- | --- |
| Button | 类型、文本、图标、disabled、loading | 触发、提交中、失败恢复 | 防重、焦点、图标名称、手机高度 |
| Field／Input | label、值、限制、帮助、错误 | 输入、失焦、提交校验 | 暂态允许、IME、错误关联、只读与禁用区别 |
| Select | 选项、值、禁用、搜索 | 打开、选中、取消 | 键盘、焦点返回、视口定位、空结果 |
| 多资源选择 | 当前集合、范围、分页与筛选 | 待选、确认、取消 | 跨页勾选、异步失效、不可用项、分页避让 |
| TagEditor | 已存值、编辑集合、长度限制 | 添加、移除、提交／取消 | 去重、中文输入、键盘、父表单未保存保护 |
| FilterBar | 暂存条件、已应用条件 | 查询、重置、Enter | 翻页重置、保留视图、例外即时筛选 |
| Pagination | 总数、页码、每页数 | 上一页、下一页、改条数 | 单页禁用、空态隐藏、删除后的有效页 |
| Dialog | 标题、内容、操作、关闭策略 | 打开、提交、关闭 | 焦点限制与恢复、背景滚动、键盘、安全区 |
| TaskProgress | 任务ID、真实状态、订阅 | 排队、进度、完成、失败、未知 | 关闭展示不重做、显示计时清理、结果核实 |
| UnsavedGuard | 基线、当前值、保存能力、目标页 | 保存、不保存、关闭 | 保存失败留页、旧草稿不误删、父级不成环 |
| ListView | 数据、筛选、排序、选择与视图 | 进入详情、返回、批量操作 | 恢复现场、行内动作不冒泡、权限变化 |
| AIWorkForm | 上下文、输入、建议、业务回调 | 生成、采用、提交、重试 | 不擅自引用背景、真实保存、输入及范围保护 |

## 6. 最小结构示例

结构示例用于说明label、错误、操作层级和命名。`data-action`只是待绑定事件，以下表单不会自动保存业务。

```html
<div class="ui-kit">
  <section class="ui-card" aria-labelledby="profile-title">
    <h2 class="ui-section-title" id="profile-title">基本信息</h2>
    <form id="profile-form">
      <div class="ui-field">
        <label for="profile-name">名称</label>
        <input class="ui-input" id="profile-name" name="name"
          required maxlength="40" aria-describedby="profile-name-help">
        <span class="ui-field-message" id="profile-name-help">
          填写便于识别的名称，最多40字
        </span>
      </div>
      <div class="ui-actions">
        <button class="ui-btn" type="button" data-action="cancel-edit">
          取消
        </button>
        <button class="ui-btn ui-btn--primary" type="submit">
          保存
        </button>
      </div>
    </form>
  </section>
</div>
```

提交失败时给该输入增加`aria-invalid="true"`，将具体错误通过`aria-describedby`关联；不要把示例固定40字当作所有业务的通用限制。控件间的组间距由目标表单布局组件控制。

弹窗优先使用项目已验证的dialog组件或原生dialog＋控制器，按通用规范实现标题、内容滚动、操作栏、焦点与Esc。不要复制一个`role="dialog"`的div而遗漏模态行为，也不要只设置`display:none`管理整个生命周期。

## 7. 可直接交给研发或AI助手的实施任务

```text
请基于本项目的产品需求实施界面，并采用配套的《界面与交互规范》和
《UI复用指南》。先读取现有工程和项目适配表，再实现共用组件与页面。

视觉：使用规范的浅色变量、字号、间距、6px控件圆角、10px卡片圆角、
12px弹窗圆角；PC主要按钮40px，手机主要点击区至少44px。

交互：每组一个主操作；查询输入与应用分开；分页与返回恢复现场；
待选集合确认前不写回；有草稿保存能力时离开只提供保存／不保存；
弹窗标题居中、关闭在右、内容独立滚动、底部不遮挡内容和分页。

实现：复用已有技术栈，不照搬视频运营的单HTML、本地存储、样本、
审批取舍、任务动效和平台能力；所有保存、发送、生成的成功状态
必须由实际业务结果决定。未接入的服务在研发说明中明确。

交付：实现正常、空、错误、禁用、提交中、失败恢复及权限变化状态；
检查1440／1024／900／768／390／320px及主要断点边界；验证键盘、
焦点、输入法、安全区、长文案及未保存保护。报告实际验证范围，
不要将静态检查或组件截图写成全流程验收。
```

## 8. 常见复用错误

| 错误 | 正确处理 |
| --- | --- |
| 把所有副操作改成文字链接 | 独立次要动作保留浅灰有边框按钮，行内操作才用轻样式 |
| 手机只缩小字号 | 重排结构、增加点击区、处理固定底栏和键盘 |
| 每个模块独立写标题栏 | 共用标题行和操作规格，避免字号／基线／hover再次不一致 |
| 直接复制整个历史CSS | 提取语义变量和必要组件，避免把失效选择器和重复覆盖带入 |
| 认为关闭进度弹窗就是取消任务 | 展示层与执行层分开，按业务定义是否可取消 |
| 用百分比或成功Toast当完成依据 | 等待真实文件、持久化或外部回执 |
| 取消选择就删掉已上传文件 | 入库与采用分开，确认文案说明后果 |
| 返回一律history.back | 按资源层级返回并恢复列表现场 |
| 在新项目复制所有视频业务限制 | 新项目填写适配表，通用组件只复用交互契约 |
| 完成样式后直接宣布可用 | 验证键盘、状态、保存、异常、权限和响应式 |

通用规范更新时直接修改正式章节；项目例外放目标项目自身规则，不把各项目的特殊流程不断追加进通用文档。
