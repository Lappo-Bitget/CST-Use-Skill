# CST Use Skill

面向 Codex 的 CST Studio Suite 电磁仿真技能，支持创建、修改、运行、诊断和验证 CST Microwave Studio 工程，包括波导、天线、超表面、RIS、周期单元、Floquet 端口及 S 参数提取。

## 主要能力

- 通过 CST 官方 Python API 自动创建和运行工程
- 配置材料、边界、端口、求解器和周期单元
- 提取并核验 S 参数、反射幅度与相位
- 复现论文中的代表性电磁模型
- 归档 `.cst` 文件及其同名外部结果目录
- 处理 CST 2024 常见路径、许可和工程创建问题

## 安装

### 方法一：使用压缩包

1. 下载仓库 Releases 或根目录中的 `CST_Use_Skill.zip`。
2. 解压后得到 `cst-use` 文件夹。
3. 将该文件夹复制到：

   ```text
   %USERPROFILE%\.codex\skills\cst-use
   ```

4. 重启 Codex。

### 方法二：克隆仓库

```powershell
git clone https://github.com/Lappo-Bitget/CST-Use-Skill.git
Copy-Item -Recurse -Force .\CST-Use-Skill\cst-use "$env:USERPROFILE\.codex\skills\cst-use"
```

## 运行依赖

- Windows
- CST Studio Suite（工作站参考针对 CST 2024）
- CST 安装目录自带的 Python API
- Codex 的本地命令与文件访问能力

`Computer Use` 插件不是核心必需依赖。纯 API 建模、求解和结果导出通常不需要它；若希望自动处理 `Retrieve License`、崩溃提示、图形界面操作或视觉核验，建议另外安装该插件。

## 使用示例

```text
使用 Cst Use 创建并运行一个 WR-90 波导仿真工程。
```

```text
使用 Cst Use 建立一个液晶可重构 RIS 周期单元，配置 Floquet 端口并导出反射相位。
```

## 注意事项

- 本仓库不包含 CST 软件或许可证。
- `.cst` 文件不一定内嵌全部结果，交付求解工程时需同时保留同名无扩展名结果目录。
- 论文复现中缺失的材料或几何参数应明确标注为假设，不应静默拟合。
- 工作站路径和 CST 安装位置可能不同，请按目标电脑实际环境调整。

