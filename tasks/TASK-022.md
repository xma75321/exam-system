# TASK-022：计时器组件

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：3 小时
- **依赖**：TASK-021
- **前置条件**：答题页面已完成

## 任务描述
实现答题计时器组件，支持倒计时显示、时间警告和超时自动提交。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `frontend/src/components/CountdownTimer.tsx` | 创建 | 倒计时组件 |
| 2 | `frontend/src/hooks/useCountdown.ts` | 创建 | 倒计时 Hook |
| 3 | `frontend/src/components/TimeWarningModal.tsx` | 创建 | 时间警告弹窗 |

## 详细要求

### frontend/src/hooks/useCountdown.ts
- 输入：结束时间（从 API 获取的 end_time）
- 状态：remainingSeconds, isWarning, isExpired
- 每秒更新剩余时间
- 计算基于服务端时间（防止客户端篡改）
  - 初始化时记录本地时间偏移量
  - 定期（每分钟）与服务端同步
- ≤ 5 分钟时 isWarning = true
- ≤ 0 时 isExpired = true 并触发回调

### frontend/src/components/CountdownTimer.tsx
- 显示格式：`MM:SS` 或 `HH:MM:SS`（超过 1 小时时）
- 正常状态：黑色文字
- 警告状态（≤ 5 分钟）：红色文字 + 闪烁
- 固定在侧栏顶部
- 始终可见（sticky 定位）

### frontend/src/components/TimeWarningModal.tsx
- 剩余 5 分钟时弹出提醒（可关闭）
- 剩余 1 分钟时再次弹出（不可关闭）
- 时间到期时显示 "时间到，系统正在自动提交..."

### 集成
- 在答题页面集成 CountdownTimer
- isExpired 时自动调用提交 API
- 提交期间禁用所有操作

## 验收标准
1. 计时器每秒更新
2. 正常时间显示黑色
3. ≤ 5 分钟时变红并闪烁
4. 5 分钟时弹出警告
5. 时间到期自动提交
6. 刷新页面后计时器从正确时间继续

## 测试方法
```bash
cd frontend
npm run dev
# 创建一个 2 分钟时长的考试
# 开始答题，验证：
# 1. 计时器显示正确
# 2. 剩余 1 分时变红
# 3. 时间到自动提交
```
