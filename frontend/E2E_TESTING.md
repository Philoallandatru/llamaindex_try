# E2E 测试指南

## 前置条件

1. **启动后端服务**
   ```bash
   cd backend
   python main.py
   ```
   后端应该运行在 `http://localhost:8000`

2. **配置 Jira（可选，用于完整测试）**
   - 访问 `http://localhost:8000/docs`
   - 使用 `/api/sources/jira/test` 测试 Jira 连接
   - 使用 `/api/sources/jira/sync` 同步一些 Issues

## 运行测试

### 1. 运行所有测试（无头模式）
```bash
cd frontend
npm run test:e2e
```

### 2. 运行测试（可视化界面）
```bash
npm run test:e2e:ui
```

### 3. 运行测试（显示浏览器）
```bash
npm run test:e2e:headed
```

### 4. 调试模式
```bash
npm run test:e2e:debug
```

## 测试覆盖范围

### 基础导航测试
- ✅ 导航到 Issues 页面
- ✅ 页面间导航（Chat / Issues / Reports / Knowledge）
- ✅ 导航菜单激活状态
- ✅ 返回按钮功能

### Issues 列表页面
- ✅ 空状态显示
- ✅ 手动输入 Issue Key
- ✅ 分析按钮启用/禁用
- ✅ 点击分析跳转到分析页面
- ✅ 显示已分析的 Issues 列表
- ✅ 点击 Issue 查看详情

### 分析页面
- ✅ 页面结构（侧边栏、主面板）
- ✅ 加载状态显示
- ✅ 错误处理（Jira 未配置）
- ✅ 返回按钮功能
- ✅ 分析结果显示（如果有数据）

### API 集成
- ✅ 调用后端 API 端点
- ✅ 错误处理

## 测试场景

### 场景 1: 无 Jira 配置
1. 启动后端（不配置 Jira）
2. 运行测试
3. 预期：导航和 UI 测试通过，分析功能显示错误

### 场景 2: 有 Jira 配置但无数据
1. 启动后端并配置 Jira
2. 不同步任何 Issues
3. 运行测试
4. 预期：所有 UI 测试通过，列表为空

### 场景 3: 完整功能测试
1. 启动后端并配置 Jira
2. 同步一些 Issues（例如：`project = PROJ`）
3. 手动分析一个 Issue（通过 Swagger UI 或前端）
4. 运行测试
5. 预期：所有测试通过，包括列表显示和详情查看

## 测试报告

测试完成后，查看 HTML 报告：
```bash
npx playwright show-report
```

## 常见问题

### 1. 测试失败：连接被拒绝
**原因**：后端未启动或端口不正确
**解决**：确保后端运行在 `http://localhost:8000`

### 2. 测试超时
**原因**：前端启动慢或后端响应慢
**解决**：增加 `playwright.config.ts` 中的 `timeout` 值

### 3. Jira 相关测试失败
**原因**：Jira 未配置
**解决**：这是预期行为，配置 Jira 后重新测试

## 手动测试步骤

如果想手动验证功能：

1. **启动服务**
   ```bash
   # Terminal 1: 后端
   cd backend
   python main.py

   # Terminal 2: 前端
   cd frontend
   npm run dev
   ```

2. **访问应用**
   打开浏览器访问 `http://localhost:5173`

3. **配置 Jira（可选）**
   - 访问 `http://localhost:8000/docs`
   - 测试 Jira 连接
   - 同步 Issues

4. **测试功能**
   - 点击 "🔍 Issues Analysis"
   - 输入 Issue Key（例如：PROJ-123）
   - 点击 "开始分析"
   - 查看分析结果
   - 返回列表查看已分析的 Issues

## 下一步

- [ ] 添加 Phase 2 测试（每日报告）
- [ ] 添加 Phase 3 测试（知识库管理）
- [ ] 添加性能测试
- [ ] 添加可访问性测试
