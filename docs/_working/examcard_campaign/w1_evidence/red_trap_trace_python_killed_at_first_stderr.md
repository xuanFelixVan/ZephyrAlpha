---
ttl: task_bound
title: "红证·陷阱哨兵：0.5s 分辨率时序（t+21.6s 写 stderr 即被杀）"
created: "2026-10-09"
sid: st-examchief-20261009
---

[19:06:35.719] === trap armed ===
[19:06:37.014] BORN pid=24340 bash.exe cmd=C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-sna
[19:06:37.014] BORN pid=28000 bash.exe cmd=C:\Program Files\Git\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-snapshots/snap
[19:06:37.014] BORN pid=35284 bash.exe cmd=C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-sna
[19:06:37.014] BORN pid=43248 bash.exe cmd=C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-sna
[19:06:37.545] BORN pid=25672 powershell.exe cmd=powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\ZephyrAlpha\.runtime\tmp\w1_pro
[19:06:37.647] BORN pid=37864 python.exe cmd=C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -c import sys,time; time
[19:06:59.253] DIED(PYTHON) pid=37864 cmd=C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -c import sys,time; time
[19:07:00.741] RUNNING-TASKS-AT-PYTHON-DEATH: ZephyrAlpha_BeltDaemon | ZephyrAlpha_DataScheduler | ZephyrAlpha_TMP_W1PROBEB | ZephyrAlpha_WorktreeDriftWatchdog | SystemSoundsService | ResolutionHost | CacheTask
[19:07:00.762] PROC-SNAPSHOT-BEGIN
[19:07:00.762]   SNAP 1848:svchost.exe::C:\Windows\system32\svchost.exe -k UnistackSvcGroup
[19:07:00.762]   SNAP 2372:ZCode.exe::E:\ZCode\ZCode.exe --type=utility --utility-sub-type=network.mojom.NetworkServic
[19:07:00.762]   SNAP 3016:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe --type=utility --utility-sub-type
[19:07:00.762]   SNAP 3048:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m zephyr.gov_
[19:07:00.762]   SNAP 3144:smartscreen.exe::C:\Windows\System32\smartscreen.exe -Embedding
[19:07:00.762]   SNAP 3808:wscript.exe::wscript.exe D:\ZephyrAlpha\scripts\launch_hidden.vbs D:\ZephyrAlpha\scripts\star
[19:07:00.762]   SNAP 4460:bash.exe::C:\Program Files\Git\bin\bash.exe -c { source '/c/Users/fanzi/.qoder-cn/shell-sn
[19:07:00.762]   SNAP 5152:ZCode.exe::E:\ZCode\ZCode.exe --type=crashpad-handler --user-data-dir=C:\Users\fanzi\AppDat
[19:07:00.762]   SNAP 5356:ctfmon.exe::/QuitInfo:0000000000000240;0000000000000244;
[19:07:00.762]   SNAP 5612:Weixin.exe::E:\软件\Weixin\Weixin.exe --user-lib-dir=E:\软件\Weixin\4.1.0.30 --no-sandbox --type
[19:07:00.762]   SNAP 5736:sihost.exe::sihost.exe
[19:07:00.762]   SNAP 5772:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe
[19:07:00.762]   SNAP 5788:svchost.exe::C:\Windows\system32\svchost.exe -k BthAppGroup -p -s BluetoothUserService
[19:07:00.762]   SNAP 5828:svchost.exe::C:\Windows\system32\svchost.exe -k UnistackSvcGroup -s CDPUserSvc
[19:07:00.762]   SNAP 5916:svchost.exe::C:\Windows\system32\svchost.exe -k LocalSystemNetworkRestricted -p -s webthreatd
[19:07:00.762]   SNAP 6012:svchost.exe::C:\Windows\system32\svchost.exe -k UnistackSvcGroup -s WpnUserService
[19:07:00.762]   SNAP 6148:pythonw.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe -m zephyr.gov
[19:07:00.762]   SNAP 7468:MSPCManagerService.exe::C:\Program Files\WindowsApps\Microsoft.MicrosoftPCManager_3.22.6.0_x64__8wekyb3d
[19:07:00.762]   SNAP 7620:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --type=renderer --e
[19:07:00.762]   SNAP 7836:taskhostw.exe::taskhostw.exe {222A245B-E637-4AE9-A93F-A59CA119A75E}
[19:07:00.762]   SNAP 9036:explorer.exe::C:\Windows\Explorer.EXE
[19:07:00.762]   SNAP 9184:ZCode.exe::E:\ZCode\ZCode.exe --no-warnings E:\ZCode\resources\tools\cua-helper\dist\window
[19:07:00.762]   SNAP 9604:SearchHost.exe::C:\Windows\SystemApps\MicrosoftWindows.Client.CBS_cw5n1h2txyewy\SearchHost.exe -
[19:07:00.762]   SNAP 9708:ChsIME.exe::C:\Windows\System32\InputMethod\CHS\ChsIME.exe -Embedding
[19:07:00.762]   SNAP 10080:StartMenuExperienceHost.exe::C:\Windows\SystemApps\Microsoft.Windows.StartMenuExperienceHost_cw5n1h2txyewy\St
[19:07:00.762]   SNAP 10416:svchost.exe::C:\Windows\system32\svchost.exe -k ClipboardSvcGroup -p -s cbdhsvc
[19:07:00.762]   SNAP 11432:RuntimeBroker.exe::C:\Windows\System32\RuntimeBroker.exe -Embedding
[19:07:00.762]   SNAP 11448:svchost.exe::C:\Windows\system32\svchost.exe -k UdkSvcGroup -s UdkUserSvc
[19:07:00.762]   SNAP 11716:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m zephyr.gov_
[19:07:00.762]   SNAP 11740:UserOOBEBroker.exe::C:\Windows\System32\oobe\UserOOBEBroker.exe -Embedding
[19:07:00.762]   SNAP 11952:LockApp.exe::C:\Windows\SystemApps\Microsoft.LockApp_cw5n1h2txyewy\LockApp.exe -ServerName:Wi
[19:07:00.762]   SNAP 12336:msedgewebview2.exe::C:\Program Files (x86)\Microsoft\EdgeWebView\Application\154.0.4258.53\msedgeweb
[19:07:00.762]   SNAP 12356:nvcontainer.exe::C:\Program Files\NVIDIA Corporation\NvContainer\nvcontainer.exe -f C:\ProgramDat
[19:07:00.762]   SNAP 12432:nvcontainer.exe::C:\Program Files\NVIDIA Corporation\NvContainer\nvcontainer.exe -f C:\ProgramDat
[19:07:00.762]   SNAP 13228:msedgewebview2.exe::C:\Program Files (x86)\Microsoft\EdgeWebView\Application\154.0.4258.53\msedgeweb
[19:07:00.762]   SNAP 13316:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --type=renderer --e
[19:07:00.762]   SNAP 13556:msedgewebview2.exe::C:\Program Files (x86)\Microsoft\EdgeWebView\Application\154.0.4258.53\msedgeweb
[19:07:00.762]   SNAP 13584:msedgewebview2.exe::C:\Program Files (x86)\Microsoft\EdgeWebView\Application\154.0.4258.53\msedgeweb
[19:07:00.762]   SNAP 13808:msedgewebview2.exe::C:\Program Files (x86)\Microsoft\EdgeWebView\Application\154.0.4258.53\msedgeweb
[19:07:00.762]   SNAP 13876:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.762]   SNAP 14176:bash.exe::C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec
[19:07:00.762]   SNAP 14232:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.762]   SNAP 14468:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.762]   SNAP 14612:msedgewebview2.exe::C:\Program Files (x86)\Microsoft\EdgeWebView\Application\154.0.4258.53\msedgeweb
[19:07:00.762]   SNAP 15188:nvsphelper64.exe::C:\Program Files\NVIDIA Corporation\NVIDIA App\ShadowPlay\nvsphelper64.exe
[19:07:00.762]   SNAP 15236:NVIDIA Overlay.exe::C:\Program Files\NVIDIA Corporation\NVIDIA App\CEF\NVIDIA Overlay.exe
[19:07:00.762]   SNAP 15752:wps.exe::E:\软件\WPS\WPS Office\12.1.0.28505\office6\wps.exe Run -Entry=EntryPoint C:\Users
[19:07:00.762]   SNAP 15992:SecurityHealthSystray.exe::C:\Windows\System32\SecurityHealthSystray.exe
[19:07:00.762]   SNAP 16108:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe D:/ZephyrAlpha
[19:07:00.762]   SNAP 16168:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.762]   SNAP 16172:sleep.exe::C:\Program Files\Git\usr\bin\sleep.exe 120
[19:07:00.762]   SNAP 16184:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.762]   SNAP 16524:RuntimeBroker.exe::C:\Windows\System32\RuntimeBroker.exe -Embedding
[19:07:00.762]   SNAP 16756:svchost.exe::C:\Windows\system32\svchost.exe -k LocalService -p -s NPSMSvc
[19:07:00.762]   SNAP 16884:NVIDIA Overlay.exe::C:\Program Files\NVIDIA Corporation\NVIDIA App\CEF\NVIDIA Overlay.exe --type=uti
[19:07:00.762]   SNAP 16892:NVIDIA Overlay.exe::C:\Program Files\NVIDIA Corporation\NVIDIA App\CEF\NVIDIA Overlay.exe --type=gpu
[19:07:00.762]   SNAP 17208:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe C:\Users\fanzi\.qoder-cn\plugins\
[19:07:00.762]   SNAP 17416:NVIDIA Overlay.exe::C:\Program Files\NVIDIA Corporation\NVIDIA App\CEF\NVIDIA Overlay.exe --type=uti
[19:07:00.762]   SNAP 17640:TextInputHost.exe::C:\Windows\SystemApps\MicrosoftWindows.Client.CBS_cw5n1h2txyewy\TextInputHost.ex
[19:07:00.762]   SNAP 17808:NVIDIA Overlay.exe::C:\Program Files\NVIDIA Corporation\NVIDIA App\CEF\NVIDIA Overlay.exe --type=ren
[19:07:00.763]   SNAP 18640:ShellExperienceHost.exe::C:\Windows\SystemApps\ShellExperienceHost_cw5n1h2txyewy\ShellExperienceHost.exe 
[19:07:00.763]   SNAP 18728:FvContainer.exe::C:\Program Files\NVIDIA Corporation\FrameViewSDK\FvContainer\FvContainer.exe -d 
[19:07:00.763]   SNAP 18784:nvrla.exe::C:\Program Files\NVIDIA Corporation\FrameViewSDK\bin\nvrla.exe
[19:07:00.763]   SNAP 19064:bash.exe::C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec
[19:07:00.763]   SNAP 19680:bash.exe::C:\Program Files\Git\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-snap
[19:07:00.763]   SNAP 19796:taskhostw.exe::taskhostw.exe $(Arg0)
[19:07:00.763]   SNAP 19804:RtkAudUService64.exe::C:\Windows\System32\DriverStore\FileRepository\realtekservice.inf_amd64_7e93164a
[19:07:00.763]   SNAP 19916:node.exe::D:\Node.js 22.x\node.exe E:\CodexCLI\node_modules\pm2\lib\Daemon.js
[19:07:00.763]   SNAP 20208:node.exe::D:\Node.js 22.x\node.exe D:\RSSHub\dist\index.mjs
[19:07:00.763]   SNAP 20364:msedgewebview2.exe::C:\Program Files (x86)\Microsoft\EdgeWebView\Application\154.0.4258.53\msedgeweb
[19:07:00.763]   SNAP 20368:bash.exe::C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec
[19:07:00.763]   SNAP 20432:DefenderSessionHelper.exe::C:\ProgramData\Microsoft\Windows Defender\Platform\4.18.26080.4-0\DefenderSessio
[19:07:00.763]   SNAP 21772:ZCode.exe::E:\ZCode\ZCode.exe E:\ZCode\resources\glm\zcode.cjs app-server --stdio --surface
[19:07:00.763]   SNAP 21884:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe --type=renderer --user-data-dir=C
[19:07:00.763]   SNAP 22132:ZCode.exe::E:\ZCode\ZCode.exe --type=gpu-process --user-data-dir=C:\Users\fanzi\AppData\Roa
[19:07:00.763]   SNAP 22492:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --type=crashpad-han
[19:07:00.763]   SNAP 22592:ZCode.exe::E:\ZCode\ZCode.exe --type=renderer --user-data-dir=C:\Users\fanzi\AppData\Roamin
[19:07:00.763]   SNAP 23228:ZCode.exe::E:\ZCode\ZCode.exe --type=utility --utility-sub-type=node.mojom.NodeService --la
[19:07:00.763]   SNAP 23240:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --type=renderer --e
[19:07:00.763]   SNAP 23252:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.EXE scripts/govern
[19:07:00.763]   SNAP 23572:crashpad_handler.exe::E:\软件\Weixin\4.1.0.30\crashpad_handler.exe --no-rate-limit --database=C:\Users\f
[19:07:00.763]   SNAP 23608:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --no-startup-window
[19:07:00.763]   SNAP 23788:updater.exe::E:\同花顺软件\同花顺\UpdateWorking\updater.exe proxy= user=NzEzNDMzNjI2 path=RTpczay7qMu
[19:07:00.763]   SNAP 24340:bash.exe::C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec
[19:07:00.763]   SNAP 24824:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -c import sys;
[19:07:00.763]   SNAP 24872:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 24956:WeChatAppEx.exe::C:\Users\fanzi\AppData\Roaming\Tencent\xwechat\xplugin\plugins\RadiumWMPF\25560\
[19:07:00.763]   SNAP 25184:RuntimeBroker.exe::C:\Windows\System32\RuntimeBroker.exe -Embedding
[19:07:00.763]   SNAP 25192:PhoneExperienceHost.exe::C:\Program Files\WindowsApps\Microsoft.YourPhone_1.26072.257.0_x64__8wekyb3d8bbw
[19:07:00.763]   SNAP 25240:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 25604:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m zephyr.gov_
[19:07:00.763]   SNAP 25672:powershell.exe::powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\ZephyrAlpha\.runtime\
[19:07:00.763]   SNAP 25692:bash.exe::C:\Program Files\Git\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-snap
[19:07:00.763]   SNAP 25736:WeChatAppEx.exe::C:\Users\fanzi\AppData\Roaming\Tencent\xwechat\xplugin\plugins\RadiumWMPF\25560\
[19:07:00.763]   SNAP 26768:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -u .runtime/tm
[19:07:00.763]   SNAP 26788:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe C:/Users/fanzi/.qoder-cn/plugins/
[19:07:00.763]   SNAP 26812:WeChatAppEx.exe::C:\Users\fanzi\AppData\Roaming\Tencent\xwechat\xplugin\plugins\RadiumWMPF\25560\
[19:07:00.763]   SNAP 27168:appshot_bare_modifier_monitor.exe::E:\Qoder CN\.qoder-versions\0.4.3\resources\bin\appshot_bare_modifier_monitor.ex
[19:07:00.763]   SNAP 27724:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 27900:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe E:/Qoder CN/.qoder-versions/0.4.3
[19:07:00.763]   SNAP 28000:bash.exe::C:\Program Files\Git\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-snap
[19:07:00.763]   SNAP 28268:Weixin.exe::E:\软件\Weixin\Weixin.exe --user-lib-dir=E:\软件\Weixin\4.1.0.30 --no-sandbox --type
[19:07:00.763]   SNAP 28936:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe --type=gpu-process --disable-gpu-
[19:07:00.763]   SNAP 29032:WeChatAppEx.exe::C:\Users\fanzi\AppData\Roaming\Tencent\xwechat\xplugin\plugins\RadiumWMPF\25560\
[19:07:00.763]   SNAP 29336:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 29532:svchost.exe::C:\Windows\system32\svchost.exe -k DevicesFlow -s DevicesFlowUserSvc
[19:07:00.763]   SNAP 29864:RuntimeBroker.exe::C:\Windows\System32\RuntimeBroker.exe -Embedding
[19:07:00.763]   SNAP 29912:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 30184:ZCode.exe::E:\ZCode\ZCode.exe --updated
[19:07:00.763]   SNAP 30248:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 30296:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 30348:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe --type=utility --utility-sub-type
[19:07:00.763]   SNAP 30456:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m zephyr.gov_
[19:07:00.763]   SNAP 30948:RuntimeBroker.exe::C:\Windows\System32\RuntimeBroker.exe -Embedding
[19:07:00.763]   SNAP 30984:bash.exe::C:\Program Files\Git\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-snap
[19:07:00.763]   SNAP 32140:dllhost.exe::C:\Windows\system32\DllHost.exe /Processid:{973D20D7-562D-44B9-B70B-5A0F49CCDF3F
[19:07:00.763]   SNAP 32696:audiodg.exe::C:\Windows\system32\AUDIODG.EXE 0x0000000000000684
[19:07:00.763]   SNAP 32792:WeChatAppEx.exe::C:\Users\fanzi\AppData\Roaming\Tencent\xwechat\xplugin\plugins\RadiumWMPF\25560\
[19:07:00.763]   SNAP 32868:bash.exe::C:\Program Files\Git\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-snap
[19:07:00.763]   SNAP 32968:DataExchangeHost.exe::C:\Windows\System32\DataExchangeHost.exe -Embedding
[19:07:00.763]   SNAP 33012:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe scripts/commit
[19:07:00.763]   SNAP 33140:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --type=gpu-process 
[19:07:00.763]   SNAP 33268:sleep.exe::C:\Program Files\Git\usr\bin\sleep.exe 21000
[19:07:00.763]   SNAP 33688:ZCode.exe::E:\ZCode\ZCode.exe --type=utility --utility-sub-type=node.mojom.NodeService --la
[19:07:00.763]   SNAP 34308:WeChatAppEx.exe::C:\Users\fanzi\AppData\Roaming\Tencent\xwechat\xplugin\plugins\RadiumWMPF\25560\
[19:07:00.763]   SNAP 34732:git.exe::git hash-object -- docs/_working/decision_map_campaign_20260924/links/L08_risk/s
[19:07:00.763]   SNAP 35284:bash.exe::C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec
[19:07:00.763]   SNAP 35704:Weixin.exe::E:\软件\Weixin\Weixin.exe --user-lib-dir=E:\软件\Weixin\4.1.0.30 --no-sandbox --type
[19:07:00.763]   SNAP 36592:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 37284:ShellHost.exe::C:\Windows\System32\ShellHost.exe
[19:07:00.763]   SNAP 37368:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe D:\ZephyrAlpha
[19:07:00.763]   SNAP 37516:bash.exe::C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec
[19:07:00.763]   SNAP 37524:Weixin.exe::E:\软件\Weixin\Weixin.exe
[19:07:00.763]   SNAP 38260:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 38472:bash.exe::C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec
[19:07:00.763]   SNAP 38476:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --type=renderer --p
[19:07:00.763]   SNAP 38492:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 38760:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 39124:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe .runtime/tmp/w
[19:07:00.763]   SNAP 39228:WeChatAppEx.exe::C:\Users\fanzi\AppData\Roaming\Tencent\xwechat\xplugin\plugins\RadiumWMPF\25560\
[19:07:00.763]   SNAP 39792:bash.exe::C:\Program Files\Git\bin\..\usr\bin\bash.exe -c { source '/c/Users/fanzi/.qoder-
[19:07:00.763]   SNAP 40084:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe E:\Qoder CN\.qoder-versions\0.4.3
[19:07:00.763]   SNAP 40092:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m zephyr.data
[19:07:00.763]   SNAP 40588:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 40848:WeChatAppEx.exe::C:\Users\fanzi\AppData\Roaming\Tencent\xwechat\xplugin\plugins\RadiumWMPF\25560\
[19:07:00.763]   SNAP 40892:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m zephyr.gov_
[19:07:00.763]   SNAP 41428:git.exe::C:\Program Files\Git\mingw64\bin\git.EXE diff --no-ext-diff --no-textconv --igno
[19:07:00.763]   SNAP 41752:ZCode.exe::E:\ZCode\ZCode.exe --type=utility --utility-sub-type=audio.mojom.AudioService --
[19:07:00.763]   SNAP 42064:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m zephyr.gov_
[19:07:00.763]   SNAP 42076:ZCode.exe::E:\ZCode\ZCode.exe E:\ZCode\resources\glm\zcode.cjs __zcode-plugin-host C:\Users
[19:07:00.763]   SNAP 42348:hxdaemonprocess.exe::E:\同花顺远航版\bin\hxdaemonprocess\hxdaemonprocess.exe proxy= main_program=aGFwcC5leG
[19:07:00.763]   SNAP 43132:updater.exe::E:\同花顺远航版\bin\UpdateWorking\updater.exe proxy= user=NzEzNDMzNjI2 path=RTpczay7qM
[19:07:00.763]   SNAP 43232:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m pre_commit 
[19:07:00.763]   SNAP 43248:bash.exe::C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec
[19:07:00.763]   SNAP 43268:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe --type=utility --utility-sub-type
[19:07:00.763]   SNAP 43492:ApplicationFrameHost.exe::C:\Windows\system32\ApplicationFrameHost.exe -Embedding
[19:07:00.763]   SNAP 43712:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe --type=utility --utility-sub-type
[19:07:00.763]   SNAP 43756:sleep.exe::C:\Program Files\Git\usr\bin\sleep.exe 16000
[19:07:00.763]   SNAP 43824:Qoder CN.exe::E:\Qoder CN\.qoder-versions\0.4.3\Qoder CN.exe --type=crashpad-handler --user-da
[19:07:00.763]   SNAP 44604:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 44844:hxdaemonprocess.exe::E:\同花顺软件\同花顺\hxdaemonprocess\hxdaemonprocess.exe proxy= main_program=aGV4aW4uZXh
[19:07:00.763]   SNAP 44924:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.763]   SNAP 45072:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --type=utility --ut
[19:07:00.763]   SNAP 45260:tail.exe::C:\Program Files\Git\usr\bin\tail.exe -1
[19:07:00.763]   SNAP 45780:YunDetectService.exe::E:\软件\BaiduNetdisk\YunDetectService.exe
[19:07:00.763]   SNAP 45968:hexinhelper.exe::1313772
[19:07:00.763]   SNAP 46712:WeChatAppEx.exe::C:\Users\fanzi\AppData\Roaming\Tencent\xwechat\xplugin\plugins\RadiumWMPF\25560\
[19:07:00.763]   SNAP 47728:QyKernel.exe::E:\IQIYI Video\LStyle\14.9.5.10287\QyKernel.exe
[19:07:00.763]   SNAP 47868:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m zephyr.gov_
[19:07:00.763]   SNAP 47880:sleep.exe::C:\Program Files\Git\usr\bin\sleep.exe 120
[19:07:00.763]   SNAP 48384:nohup.exe::C:\Program Files\Git\usr\bin\nohup.exe python -u .runtime/tmp/bcure/ti_shard_sel
[19:07:00.763]   SNAP 48548:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --type=renderer --p
[19:07:00.764]   SNAP 48768:WeChatAppEx.exe::C:\Users\fanzi\AppData\Roaming\Tencent\xwechat\xplugin\plugins\RadiumWMPF\25560\
[19:07:00.764]   SNAP 49092:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe D:\ZephyrAlpha
[19:07:00.764]   SNAP 50340:python.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe -m zephyr.gov_
[19:07:00.764]   SNAP 50488:bash.exe::C:\Program Files\Git\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-snap
[19:07:00.764]   SNAP 50768:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.764]   SNAP 50920:sleep.exe::C:\Program Files\Git\usr\bin\sleep.exe 60
[19:07:00.764]   SNAP 51352:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --type=renderer --p
[19:07:00.764]   SNAP 52276:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.764]   SNAP 52852:bash.exe::C:\Program Files\Git\bin\bash.exe -c { source '/c/Users/fanzi/.qoder-cn/shell-sn
[19:07:00.764]   SNAP 53156:powershell.exe::C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionP
[19:07:00.764]   SNAP 56352:tail.exe::C:\Program Files\Git\usr\bin\tail.exe -1
[19:07:00.764]   SNAP 56580:msedge.exe::C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --type=utility --ut
[19:07:00.764]   SNAP 56640:pythonw.exe::C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe D:\ZephyrAlph
[19:07:00.764]   SNAP 56700:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.764]   SNAP 56708:conhost.exe::C:\Windows\System32\conhost.exe --headless -- C:\Windows\System32\WindowsPowerSh
[19:07:00.764]   SNAP 57020:mpc-be64.exe::E:\MPC-BE播放器\mpc-be64.exe
[19:07:00.764]   SNAP 58080:conhost.exe::\??\C:\Windows\system32\conhost.exe 0x4
[19:07:00.764]   SNAP 58244:bash.exe::C:\Program Files\Git\bin\..\usr\bin\bash.exe -c { source '/c/Users/fanzi/.qoder-
[19:07:00.764] PROC-SNAPSHOT-END
[19:07:03.394] DIED(PS) pid=25672 cmd=powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\ZephyrAlpha\.runtime\tmp\w1_pro
[19:08:39.259] DIED(PS) pid=28000 cmd=C:\Program Files\Git\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-snapshots/snap
[19:08:39.259] DIED(PS) pid=43248 cmd=C:\Program Files\Git\bin\..\usr\bin\bash.exe -c . /c/Users/fanzi/.zcode/cli/exec/shell-sna
[19:09:06.336] === trap closed python_death_delta=1791544019.254 ps_death_delta=1791544023.395 ===
