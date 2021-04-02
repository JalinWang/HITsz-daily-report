# HITsz-daily-report

基于 Github Action 的定时HITsz疫情上报脚本，开箱即用
感谢 [@JellyBeanXiewh](https://github.com/JellyBeanXiewh/) 提供原始脚本和 idea。

[疫情上报系统入口](http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/yqxx)

使用方法：
- fork 仓库
- 开启 Action（详细步骤见后文）
- 设置仓库的 Action Secrets，添加用户名 username、密码 password 和可选的 API_KEY（详细步骤见后文）
- 每天早上 7:00 (UTC 23:00) 可自动定时运行，如果填写 API_KEY，即可在微信上收到运行结果推送

消息推送Key申请地址：[Server酱](http://sc.ftqq.com/)

据说 fork 的仓库会默认关闭 Action 的执行，需要在仓库设置里打开：
![启用Action的步骤1](./image/enable1.png)
![启用Action的步骤1](./image/enable2.png)

设置仓库的 Action Secrets，添加用户名 username、密码 password 和可选的 API_KEY：
![添加Action Secret的步骤](./image/instruction.png)