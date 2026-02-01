# 自动化训练启动脚本
# 在后台运行训练流水线

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 AI游戏机器人 - 自动化训练流水线" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python环境
Write-Host "检查环境..." -ForegroundColor Yellow
conda activate Ai-Gameplay-Bot

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 无法激活conda环境 Ai-Gameplay-Bot" -ForegroundColor Red
    exit 1
}

# 显示流水线信息
Write-Host ""
Write-Host "流水线将执行以下步骤:" -ForegroundColor Green
Write-Host "  1. 数据增强 (约15-30分钟)" -ForegroundColor White
Write-Host "     - 为动作4和5各生成约1000个增强样本" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. 模型训练 (约2-4小时)" -ForegroundColor White
Write-Host "     - 使用类别权重平衡训练" -ForegroundColor Gray
Write-Host "     - 100个epoch，early stopping=15" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. 模型评估 (约5分钟)" -ForegroundColor White
Write-Host "     - 完整测试集评估" -ForegroundColor Gray
Write-Host "     - 生成各动作类别准确率报告" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. 模型备份 (约1分钟)" -ForegroundColor White
Write-Host ""

# 估计时间
Write-Host "预计总耗时: 3-5小时" -ForegroundColor Cyan
Write-Host "日志保存位置: logs\" -ForegroundColor Cyan
Write-Host ""

# 确认
$confirmation = Read-Host "是否开始执行? (Y/N)"
if ($confirmation -ne 'Y' -and $confirmation -ne 'y') {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "启动中..." -ForegroundColor Green
Write-Host ""

# 运行流水线
conda activate Ai-Gameplay-Bot
python scripts/auto_train_pipeline.py

# 检查结果
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ 流水线执行完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步:" -ForegroundColor Cyan
    Write-Host "  1. 查看 logs\ 目录中的日志文件" -ForegroundColor White
    Write-Host "  2. 检查模型评估结果" -ForegroundColor White
    Write-Host "  3. 使用以下命令在游戏中测试:" -ForegroundColor White
    Write-Host "     python scripts/real_time_controller.py --model 'models/transformer/transformer_model.pth'" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "⚠️ 流水线执行遇到问题" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "请查看日志文件了解详情: logs\" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
