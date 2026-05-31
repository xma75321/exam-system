# TASK-007：文件上传 API

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：3 小时
- **依赖**：TASK-001
- **前置条件**：后端项目初始化完成

## 任务描述
实现 Word 文件上传接口，验证文件格式和大小，保存到服务器磁盘。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/routers/upload.py` | 创建 | 上传路由 |
| 2 | `backend/app/services/upload_service.py` | 创建 | 文件存储服务 |
| 3 | `backend/app/schemas/upload.py` | 创建 | 上传响应模型 |
| 4 | `backend/tests/test_upload.py` | 创建 | 上传测试 |
| 5 | `backend/uploads/.gitkeep` | 创建 | 上传目录占位 |

## 详细要求

### backend/app/routers/upload.py
- `POST /api/upload`：接收 multipart/form-data
- 验证文件扩展名为 .docx
- 验证文件大小 ≤ 10MB
- 调用 upload_service 保存文件
- 返回文件信息和解析后的题目（TASK-008 实现解析，此处返回占位）

### backend/app/services/upload_service.py
- `save_upload(file: UploadFile)`：保存文件到 UPLOAD_DIR
- 生成唯一文件名（UUID + 原始扩展名）
- 返回保存后的文件路径和原始文件名
- 检查文件头是否为有效 docx（PK 开头的 zip 格式）

### backend/app/schemas/upload.py
- `UploadResponse`：filename, file_path, file_size, total_count, questions（占位空列表）

### backend/tests/test_upload.py
- 上传 .docx 文件返回 200
- 上传非 .docx 文件返回 400
- 上传超过 10MB 文件返回 400
- 无文件上传返回 422

## 验收标准
1. `POST /api/upload` 可接收文件上传
2. 上传 .docx 文件成功保存到 `backend/uploads/` 目录
3. 上传非 .docx 文件返回 400 错误
4. 文件名包含 UUID，不会重复
5. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_upload.py -v

# 手动测试
# 创建一个测试 .docx 文件
echo "test" > test.docx  # 注意：实际需使用 python-docx 创建
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.docx"
# 预期：200，返回文件信息
```
