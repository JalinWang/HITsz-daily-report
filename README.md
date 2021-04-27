# HITsz-daily-report

基于Github Action的定时HITsz疫情上报脚本，开箱即用
感谢 @JellyBeanXiewh 提供原始脚本和idea。

[疫情上报系统入口](http://xgsm.hitsz.edu.cn/zhxy-xgzs/xg_mobile/xs/yqxx)

## 使用方法：
- fork仓库
- 设置仓库的action secret，添加用户名username、密码password和可选的API_KEY（详细步骤见后文）
- 开启Action（详细步骤见后文）
- 每天早上7:00（UTC 23:00)可自动定时运行。你可以根据后文内容，设置邮件或微信提醒


消息推送Key申请地址：[Server酱](http://sc.ftqq.com/)

设置仓库的action secret，添加用户名username、密码password和可选的API_KEY：

| Name          | Value                                |
| ------------- | ------------------------------------ |
| username      | HITsz统一身份认证密码 （学号）         |
| password      | HITsz统一身份认证密码                 |
| API_KEY       | 可选。server酱推送的sckey, 或发送电子邮件的密码/Key      |
| MAIL_TO       | 可选。电子邮件信息，格式"服务器[:端口[U]]:用户名(邮箱)"                   |

![添加Action Secret的步骤](./image/instruction.png)

据说fork的仓库会默认关闭action的执行，需要在仓库设置里打开：
![启用Action的步骤1](./image/enable1.png)
![启用Action的步骤1](./image/enable2.png)

以上步骤都完工后可以手动运行一次工作流，验证是否可以正常工作
![手动运行](./image/test_run.png)

## 上报情况提醒

为了防止脚本突然挂了等情况发生，可设置电子邮件或微信提醒。

### 电子邮件提醒

1. 设定Secrets的`MAIL_TO`字段，格式`服务器[:端口[U]]:用户名(邮箱)`，服务器域名和地址可参考[这篇博客](https://blog.csdn.net/zhangge3663/article/details/104293945/)。如果不设置端口，则尝试使用默认。如果加'U'则不使用TLS。
2. 设定Secrets的`API_KEY`为你的邮箱账户密码，或是SMTP对应的API_KEY。

### 微信提醒

微信提醒基于[Server酱](http://sc.ftqq.com/)，将Server酱中获取的API_KEY后填写到Secrets的`API_KEY`即可。