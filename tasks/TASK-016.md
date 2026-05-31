# TASK-016：前端上传页面

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：6 小时
- **依赖**：TASK-002, TASK-013
- **前置条件**：前端项目初始化完成，题库入库 API 可用

## 任务描述
实现前端 Word 文件上传页面，支持拖拽上传、解析预览和确认入库。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `frontend/src/app/upload/page.tsx` | 创建 | 上传页面 |
| 2 | `frontend/src/components/FileUploader.tsx` | 创建 | 文件上传组件 |
| 3 | `frontend/src/components/ParsePreview.tsx` | 创建 | 解析预览组件 |
| 4 | `frontend/src/hooks/useUpload.ts` | 创建 | 上传状态 Hook |
| 5 | `frontend/src/types/question.ts` | 创建 | 题目类型定义 |

## 详细要求

### frontend/src/types/question.ts
- `QuestionType`：'single' | 'multi' | 'judge' | 'fill' | 'essay'
- `Option`：label, content, is_correct?
- `ParsedQuestion`：temp_id, type, content, options?, answer, score, explanation?
- `ParseResult`：filename, questions, total_count, type_summary
- `Question`：id, type, content, score, created_at（数据库记录）

### frontend/src/components/FileUploader.tsx
- 拖拽上传区域（虚线边框）
- 点击选择文件按钮
- 支持格式提示文字
- 上传中显示进度条
- 文件大小验证（客户端，≤ 10MB）
- 文件格式验证（仅 .docx）

### frontend/src/components/ParsePreview.tsx
- 题型统计卡片（显示每种题型数量）
- 题目列表（可展开/收起）
  - 题型标签（颜色区分）
  - 题目内容摘要
  - 选项列表（选择题）
  - 答案显示
- "确认入库" 按钮
- "重新上传" 按钮
- 入库中显示加载状态

### frontend/src/hooks/useUpload.ts
- 状态：file, uploading, parseResult, saving
- 方法：uploadFile, confirmSave, reset
- 上传进度追踪

### frontend/src/app/upload/page.tsx
- 左右布局：左侧上传，右侧预览
- 未上传时：右侧显示引导提示
- 上传后：右侧显示解析结果
- 入库成功：Toast 提示，可跳转到题库

## 验收标准
1. 访问 `/upload` 显示上传页面
2. 拖拽 .docx 文件到上传区域触发上传
3. 点击按钮选择文件触发上传
4. 非 .docx 文件被拒绝（客户端提示）
5. 上传后右侧显示解析预览
6. 题型统计正确显示
7. 点击"确认入库"成功保存到数据库
8. 入库成功后有 Toast 提示

## 测试方法
```bash
cd frontend
npm run dev
# 1. 访问 http://localhost:3000/upload
# 2. 上传一个 .docx 试卷文件
# 3. 验证解析预览正确显示
# 4. 点击"确认入库"
# 5. 验证数据库中增加了题目记录
```
