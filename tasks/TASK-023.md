# TASK-023：自动保存机制

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：3 小时
- **依赖**：TASK-021, TASK-020
- **前置条件**：答题页面和答题 API 已完成

## 任务描述
实现答题答案的自动保存机制，防止答案丢失。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `frontend/src/hooks/useAutoSave.ts` | 创建 | 自动保存 Hook |
| 2 | `frontend/src/components/SaveIndicator.tsx` | 创建 | 保存状态指示器 |

## 详细要求

### frontend/src/hooks/useAutoSave.ts
- 定时器：每 30 秒自动保存
- 条件触发：
  - 答案发生变化时启动 30 秒倒计时
  - 切题时立即保存
  - 页面关闭前保存（beforeunload 事件）
- 状态：idle, saving, saved, error
- 防抖：连续修改时重置计时器
- 失败重试：最多重试 3 次，间隔递增
- 方法：
  - `markDirty()`：标记答案有变更
  - `saveNow()`：立即保存
  - `startAutoSave()`：启动自动保存
  - `stopAutoSave()`：停止自动保存

### frontend/src/components/SaveIndicator.tsx
- 状态显示：
  - idle：不显示
  - saving：旋转图标 + "保存中..."
  - saved：绿色对号 + "已保存"
  - error：红色感叹号 + "保存失败，点击重试"
- 位置：答题区底部或侧栏底部
- 点击 error 状态可手动重试

### 集成到答题页面
- 答题页面使用 useAutoSave Hook
- 切题时调用 markDirty()
- AnswerInput 变更时调用 markDirty()
- 提交前先调用 saveNow() 确保最新答案已保存

## 验收标准
1. 修改答案后 30 秒内自动保存
2. 切题时自动保存
3. 保存状态正确显示
4. 保存失败时显示错误提示
5. 刷新页面后答案不丢失
6. 关闭页面时触发保存

## 测试方法
```bash
cd frontend
npm run dev
# 1. 开始考试
# 2. 作答几道题
# 3. 等待 30 秒，验证"已保存"提示
# 4. 刷新页面，验证答案仍在
# 5. 断网后修改答案，验证"保存失败"提示
```
