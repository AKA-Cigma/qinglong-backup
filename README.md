# qinglong-backup

- 将[青龙](https://github.com/whyour/qinglong)的基本配置文件及脚本备份至阿里网盘&阿里网盘自动签到
- 鸣谢[原项目](https://github.com/Ukenn2112/qinglong_Backup)作者@Ukenn2112

# 使用

- 将 `aligo` 添加 Python3 依赖至 qinglong 面板

  - `依赖管理` --> `Python3` --> `新建依赖` --> 名称内输入 `aligo==6.0.4` 保存（6.1.*版本接口改了会报错） --> 等待安装完成

- 拉库命令

  - 可以直链github/国外机:   `ql repo https://github.com/AKA-Cigma/qinglong-backup.git`

- 第一次使用

  - 请先手动运行一次复制登录二维码链接扫码登录阿里云盘

# 变量

  - `QLBK_EXCLUDE_NAMES` 排除备份`/ql/[data/]`下的目录

    默认为 `['log', 'syslog', '.git', '.github', 'node_modules', 'backups', '.pnpm-store']`，不需要是列表形式，只要包含要排除的目录名字就可以，比如`log, syslog, .git, .github, node_modules, backups, .pnpm-store`

  - `QLBK_BACKUPS_PATH` 备份目录`/ql/[data/]<QLBK_BACKUPS_PATH>`
  
    默认为 `backups`
    
  - `QLBK_UPLOAD_PATH` 网盘上传目录`<QLBK_UPLOAD_PATH>`
  
    默认为 `backups`，如网盘中不存在会自动在`文件（PC端为全部文件）/备份文件`下创建，多层目录`/`连接
    
  - `QLBK_MAX_FLIES` 本地最大备份数

    默认为 `5`

  - `QLBK_CLOUD_MAX_FLIES` 云端最大备份数

    默认为 `100`

  - `EXEC_SIGN_IN` 是否进行自动签到

    默认为 `True`

# 恢复备份

  1. 解压缩备份文件 qinglong_xxx.tar.gz

  2. 提取名称为 `ql` 的文件夹

  3. 删除之前的qinglong容器重新创建映射以下对应目录：

  - qinglong 2.11.3 及其之前版本

        ```
        /ql/config
        /ql/db
        /ql/repo
        /ql/raw
        /ql/scripts
        /ql/jbot (如有jbot)
        /ql/ninja (如有ninja)
        ```
  - qinglong 2.12.0 及其之后版本

        ```
        /ql/data
        ```

   例 qinglong 2.11.3（docker-compose） `+ 号后为可选,如果备份文件里有这些文件则加上`：

   ```diff
   version: "3"
   services:
     qinglong:
       image: whyour/qinglong:latest
       container_name: qinglong
       restart: unless-stopped
       tty: true
       ports:
         - 5700:5700
   +     - 5701:5701 (如有ninja)
       environment:
         - ENABLE_HANGUP=true
         - ENABLE_WEB_PANEL=true
       volumes:
         - /ql/config:/ql/config
         - /ql/log:/ql/log
         - /ql/db:/ql/db
         - /ql/repo:/ql/repo
         - /ql/raw:/ql/raw
         - /ql/scripts:/ql/scripts
   +     - /ql/jbot:/ql/jbot  (如有jbot)
   +     - /ql/jbot:/ql/jbot  (如有ninja)
   ```

   例 qinglong 2.11.3（docker-run） `+ 号后为可选 解释同上`：

   ```diff
   docker run -dit \
     -v $PWD/ql/config:/ql/config \
     -v $PWD/ql/log:/ql/log \
     -v $PWD/ql/db:/ql/db \
     -v $PWD/ql/repo:/ql/repo \
     -v $PWD/ql/raw:/ql/raw \
     -v $PWD/ql/scripts:/ql/scripts \
   + -v $PWD/ql/jbot:/ql/jbot \
   + -v $PWD/ql/ninja:/ql/ninja \
     -p 5700:5700 \
   + -p 5701:5701 \
     --name qinglong \
     --hostname qinglong \
     --restart unless-stopped \
     whyour/qinglong:latest
   ```

   例 qinglong 2.12.0 及其之后版本（docker-run），会将本地路径映射到容器，可修改版本分支：

   ```diff
   docker run -dit \
     -v $PWD/ql/data:/ql/data \
     -p 5700:5700 \
     -e QlBaseUrl="/" \
     -e QlPort="5700" \
     --name qinglong \
     --hostname qinglong \
     --restart unless-stopped \
     whyour/qinglong:debian
   ```

# 感谢

  - [aligo SDK 提供上传阿里网盘支持](https://github.com/foyoux/aligo)
