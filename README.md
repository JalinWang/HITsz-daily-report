# HITsz-daily-report

基于 Github Action 的定时 HITsz 疫情上报脚本，开箱即用  
感谢 @JellyBeanXiewh 提供原始脚本和 idea 。

[疫情上报系统入口](http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/yqxx)

## 使用方法
1. `fork` 仓库
2. 设置仓库的 Action Secret ，添加用户名 `username` 、密码 `password` 和可选的 `API_KEY`
   | Name          | Value                                |
   | :-------------: | :------------------------------------: |
   | username      | HITsz 统一身份认证用户名 （学号）         |
   | password      | HITsz 统一身份认证密码                 |
   | API_KEY       | [Server 酱](http://sc.ftqq.com/)推送的 sckey                   |
3. 开启 Action （详细步骤见后文）
4. 每天早上 7:00（UTC 23:00) 可自动定时运行，如果填写 `API_KEY` ，即可在微信上收到运行结果推送

### 如何开启 Action

![添加 Action Secret 的步骤](./image/instruction.png)

据说 `fork` 的仓库会默认关闭 Action 的执行，需要在仓库设置里打开：
![启用 Action 的步骤 1](./image/enable1.png)
![启用 Action 的步骤 2](./image/enable2.png)

以上步骤都完工后可以手动运行一次工作流，验证是否可以正常工作
![手动运行](./image/test_run.png)
