
---
[task: cf5cdb2a-5987-4ae1-a338-9841c9ce0fcc] 2026-09-14 21:22:42

[steps: 63 actions]
1. [thinking] Let me analyze the current state of the page. I can see a Shenzhen Government Data Open Platform interface testing console. There's a dropdown list showing various API interfaces. I need to: 1. Click ...
   get_current_state
2. ![screenshot_2](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2gav1v47eadhn9cbqp_20260914211637.jpeg)
   [thinking] 我可以看到接口选择下拉框已经打开，显示了多个接口选项。我需要逐一选择每个接口并提取其名称和请求地址。让我先从第一个接口开始。 当前可见的接口有： 1. 历史上各时段历史气候 2. 月平均气温逐日累计值表 3. 逐1月逐-前段 4. 逐1月逐-前段气候 5. 逐1月逐-前段气候 6. 逐1月逐-运输 7. 逐1月逐-通定资产投资 8. 逐1月逐-国际经济贸易 9. 统计科技 10. 规划馆数据_实验...
   left_click → [428,456]
3. ![screenshot_3](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2ge1l3towadjar8kap_20260914211645.jpeg)
   [thinking] 已选择第1个接口：**历史上各时段历史气候**，请求地址为：`https://opendata.sz.gov.cn/api/29200_00003514/1/service.xhtml` 现在选择下一个接口。让我点击接口选择下拉框：
   left_click → [495,423]
4. ![screenshot_4](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2ggh9ck69adl7zkte5_20260914211650.jpeg)
   [thinking] 下拉框再次打开了。现在我需要选择第二个接口。让我点击第二个选项"月平均气温逐日累计值表"：
   left_click → [428,484]
5. ![screenshot_5](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2girw1qkbadnz07unh_20260914211655.jpeg)
   [thinking] It seems like the page didn't change - the interface name still shows "历史上各时段历史气候" and the request URL is still the same. Let me check if my click actually selected a different item. Looking at the dr...
   left_click → [495,423]
6. ![screenshot_6](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2glkq7ncmadp5gf2e8_20260914211701.jpeg)
   [thinking] 下拉框已打开。我可以看到列表中的接口。让我仔细看一下这些接口名称，它们有些模糊。让我用extract_content来获取更清晰的信息：
   extract_content
7. ![screenshot_7](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2go2tbksvadvqvryry_20260914211722.jpeg)
   [thinking] Now I can see the dropdown list clearly. The extracted content shows 17 interfaces visible in the dropdown. But the task says there are about 47 interfaces total, so I'll need to scroll down in the dr...
   left_click → [428,456]
8. ![screenshot_8](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2gz2x10arae4bs5d3n_20260914211731.jpeg)
   [thinking] 第1个接口已选中： - **接口名称**: 历史上登陆我国的气旋 - **请求地址**: https://opendata.sz.gov.cn/api/29200_00003514/1/service.xhtml 现在选择第2个接口：
   left_click → [495,423]
9. ![screenshot_9](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2h1bazou6aeckbnwqc_20260914211736.jpeg)
   [thinking] The dropdown is open again. I need to select the second item "历年台风的中英文对照表". Let me click on it precisely.
   left_click → [428,484]
10. ![screenshot_10](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2h469m7baaeebo4io3_20260914211742.jpeg)
   [thinking] The page still shows "历史上登陆我国的气旋" - the selection didn't change. It seems like the click isn't registering properly on the dropdown items. Let me try a different approach - maybe I need to use the sel...
   left_click → [495,423]
11. ![screenshot_11](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2h6z3svojaehigkgcs_20260914211748.jpeg)
   [thinking] The dropdown is open. Let me try using the select_dropdown_option action to select the second item "历年台风的中英文对照表".
   select_dropdown_option
12. ![screenshot_12](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2h9m0i1bbaek9bau30_20260914211754.jpeg)
   [thinking] The page still shows "历史上登陆我国的气旋" - the selection didn't change. The select_dropdown_option didn't work either. Let me look more carefully at the page structure. Looking at the screenshot, I notice th...
   left_click → [495,423]
13. ![screenshot_13](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2hctjn1sqaem3im14j_20260914211800.jpeg)
   [thinking] The dropdown is open. Let me try clicking on the second item "历年台风的中英文对照表" more precisely. Looking at the dropdown, the items appear to be at different y-coordinates. Let me try clicking at a slightly...
   double_click
14. ![screenshot_14](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2hfs815rsaeuqs81mh_20260914211807.jpeg)
   [thinking] Still showing "历史上登陆我国的气旋". The clicks aren't working to select different items. Let me try a completely different approach. Maybe I need to use JavaScript to interact with this dropdown, or maybe I n...
   key → Escape
15. ![screenshot_15](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2hiaowiaaaexigqb0l_20260914211812.jpeg)
   [thinking] OK, the dropdown is now closed. The page still shows "历史上登陆我国的气旋" with URL `https://opendata.sz.gov.cn/api/29200_00003514/1/service.xhtml`. Let me try a different approach. Instead of trying to click ...
   left_click → [495,423]
16. ![screenshot_16](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2hko8dwbhaezaot8by_20260914211817.jpeg)
   [thinking] Good, the dropdown is open. Now let me try using the Up arrow key to move to the second item and then press Enter to select it.
   key → ArrowUp Enter
17. ![screenshot_17](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2hnbhwtwcaf25pfczz_20260914211823.jpeg)
   [thinking] The page still shows "历史上登陆我国的气旋" - the selection didn't change. The keyboard navigation also didn't work. This is very frustrating. Let me think about this differently. Maybe the dropdown items are n...
   left_click → [495,423]
18. ![screenshot_18](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2hqd4ckxlaf4h3a411_20260914211830.jpeg)
   [thinking] The dropdown is open again. Let me try clicking on the second item "历年台风的中英文对照表" at a different position. Looking at the dropdown, the second item starts with "历" character. Let me try clicking at x=4...
   left_click → [406,484]
19. ![screenshot_19](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2htnnhh22afhxns61i_20260914211838.jpeg)
   [thinking] The dropdown closed but the selection still shows "历史上登陆我国的气旋". The clicks don't seem to be selecting different items. Let me try a completely different approach. Let me try to use JavaScript to inspe...
   left_click → [495,423]
20. ![screenshot_20](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2hx8jdjx5afl87fe4r_20260914211845.jpeg)
   [thinking] The dropdown is open. Let me try clicking on the third item "统计月报-物价" at y≈371.
   left_click → [421,515]
21. ![screenshot_21](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2hzgd6qisafnktwewk_20260914211850.jpeg)
   [thinking] The selection still shows "历史上登陆我国的气旋". My clicks on the dropdown items are not working. Let me try a completely different approach. Let me try to use JavaScript to interact with the page. I'll try to...
   left_click → [589,423]
22. ![screenshot_22](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2i34wsoz7afpihza3n_20260914211858.jpeg)
   [thinking] The dropdown is open again. Let me try a completely different approach. Let me try to use JavaScript to find and click the dropdown items. I'll try to use the browser console to execute JavaScript. Ac...
   hover
23. ![screenshot_23](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2i5hg2zt9ag0jn1o0j_20260914211902.jpeg)
   [thinking] Let me try clicking after hovering.
   left_click → [428,484]
24. ![screenshot_24](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2i7rb36sdag29ea20i_20260914211908.jpeg)
   [thinking] The selection still shows "历史上登陆我国的气旋" with the same URL. The hover+click approach didn't work either. Let me try a completely different approach. Let me try to use JavaScript to find the dropdown ele...
   key → F12
25. ![screenshot_25](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2iaaltot0ag5gindzc_20260914211914.jpeg)
   [thinking] The F12 didn't seem to open developer tools (or they opened but aren't visible in the screenshot). Let me try a different approach. Let me try to use JavaScript to find the dropdown elements. I'll try...
   key → ctrl+shift+j
26. ![screenshot_26](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2idlbhqj5ag9ea8ovu_20260914211920.jpeg)
   [thinking] The console didn't open either. Let me try a different approach. Let me try to use JavaScript to find the dropdown elements by navigating to a javascript: URL. Actually, I can't do that directly in th...
   left_click → [495,423]
27. ![screenshot_27](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2ifq7nhksagdea6rdz_20260914211925.jpeg)
   [thinking] The dropdown is open. Let me try using Tab key to navigate to the second item and then press Enter.
   key → Tab Enter
28. ![screenshot_28](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2ihs6sj1iageg57d5f_20260914211929.jpeg)
   [thinking] The dropdown is still open and the selection still shows "历史上登陆我国的气旋". The Tab+Enter approach didn't work either. Let me try a completely different approach. Let me try to use JavaScript to find and c...
   key → ArrowDown Enter
29. ![screenshot_29](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2ikbk7lvragkaq67px_20260914211934.jpeg)
   [thinking] Excellent! The ArrowDown+Enter approach worked! The page now shows:- 接口列表: 历年台风的中英文对照表 - 请求地址: https://opendata.sz.gov.cn/api/29200_00003515/1/service.xhtmlSo the second interface is: - 接口名称: 历年台风的中英文...
   key → ArrowDown Enter
30. ![screenshot_30](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2in8fedngagmjkgwvl_20260914211941.jpeg)
   [thinking] The dropdown is open and I can see "统计月报-物价" is highlighted. Let me press Enter to select it.
   key → Enter
31. ![screenshot_31](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2ip2q5rbmagnlxg7un_20260914211945.jpeg)
   [thinking] 第3个接口已选中： - **接口名称**: 统计月报-物价 - **请求地址**: https://opendata.sz.gov.cn/api/29200_03023837/1/service.xhtml 现在继续选择第4个接口。我需要先点击下拉框打开它，然后用ArrowDown+Enter来选择下一个。
   left_click → [495,423]
32. ![screenshot_32](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2irh06xagagog5b3dz_20260914211951.jpeg)
   [thinking] The dropdown is open and "统计月报-物价" is highlighted. I need to press ArrowDown to move to the next item and then Enter to select it.
   key → ArrowDown Enter
33. ![screenshot_33](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2itk16ujzagrochjpm_20260914211954.jpeg)
   [thinking] 第4个接口已选中： - **接口名称**: 统计月报-财政金融 - **请求地址**: https://opendata.sz.gov.cn/api/29200_
   left_click → [495,423]
34. ![screenshot_34](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2iwcw9blkagsgqthtw_20260914212001.jpeg)
   [thinking] The dropdown is open and "统计月报-财政金融" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
35. ![screenshot_35](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2iy9ya12lagvhtocv3_20260914212005.jpeg)
   [thinking] 第5个接口已选中： - **接口名称**: 统计月报-对外贸易 - **请求地址**: https://opendata.sz.gov.cn/api/29200_03023797/1/service.xhtml 继续选择第6个接口。
   left_click → [495,423]
36. ![screenshot_36](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2j068wpc3agwgdgxb7_20260914212010.jpeg)
   [thinking] The dropdown is open and "统计月报-对外贸易" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
37. ![screenshot_37](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2j23zigp1agxbe9sae_20260914212013.jpeg)
   [thinking] 第6个接口已选中： - **接口名称**: 统计月报-运输 - **请求地址**: https://opendata.sz.gov.cn/api/29200_03023771/1/service.xhtml 继续选择第7个接口。
   left_click → [495,423]
38. ![screenshot_38](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2j425nwwkagy0krnyw_20260914212018.jpeg)
   [thinking] The dropdown is open and "统计月报-运输" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
39. ![screenshot_39](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2j6b1yhs8agz8t39ls_20260914212023.jpeg)
   [thinking] 第7个接口已选中： - **接口名称**: 统计月报-固定资产投资 - **请求地址**: https://opendata.sz.gov.cn/api/29200_03023757/1/service.xhtml 继续选择第8个接口。
   left_click → [495,423]
40. ![screenshot_40](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2j89bxix0ah0uyadjc_20260914212027.jpeg)
   [thinking] The dropdown is open and "统计月报-固定资产投资" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
41. ![screenshot_41](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2jantr2ieah1s0u02l_20260914212032.jpeg)
   [thinking] 第8个接口已选中： - **接口名称**: 统计月报-国民经济核算 - **请求地址**: https://opendata.sz.gov.cn/api/29200_03023707/1/service.xhtml 继续选择第9个接口。
   left_click → [495,423]
42. ![screenshot_42](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2jcm2ht6xah4swfjsy_20260914212037.jpeg)
   [thinking] The dropdown is open and "统计月报-国民经济核算" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
43. ![screenshot_43](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2jf2emgd8ah57yqosn_20260914212042.jpeg)
   [thinking] 第9个接口已选中： - **接口名称**: 统计快报 - **请求地址**: https://opendata.sz.gov.cn/api/29200_03023659/1
   left_click → [495,423]
44. ![screenshot_44](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2jhf617b5ah67neeup_20260914212047.jpeg)
   [thinking] The dropdown is open and "统计快报" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
45. ![screenshot_45](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2jjglego8ah74pt0tp_20260914212051.jpeg)
   [thinking] 第10个接口已选中： - **接口名称**: 预报预警数据_灾害性天气预警 - **请求地址**: https://opendata.sz.gov.cn/api/589826355/1/service.html 继续选择第11个接口。
   left_click → [495,423]
46. ![screenshot_46](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2jlupthysah8u47ry1_20260914212057.jpeg)
   [thinking] The dropdown is open and "预报预警数据_灾害性天气预警" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
47. ![screenshot_47](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2jny6zzmyah92f0izf_20260914212101.jpeg)
   [thinking] 第11个接口已选中： - **接口名称**: 二手房成交信息（按日统计） - **请求地址**: https://opendata.sz.gov.cn/api/29200_01903517/1/service.xhtml 继续选择第12个接口。
   left_click → [495,423]
48. ![screenshot_48](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2jq00tmrhahciozgpl_20260914212106.jpeg)
   [thinking] The dropdown is open and "二手房成交信息（按日统计）" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
49. ![screenshot_49](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2js5bw0ipahd2mhww2_20260914212110.jpeg)
   [thinking] 第12个接口已选中： - **接口名称**: 一手商品房成交信息（按日统计） - **请求地址**: https://opendata.sz.gov.cn/api/29200_01903517/1/service.xhtml 继续选择第13个接口。
   left_click → [495,423]
50. ![screenshot_50](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2ju9kiuprahesj6dv3_20260914212115.jpeg)
   [thinking] The dropdown is open and "一手商品房成交信息（按日统计）" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
51. ![screenshot_51](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2jwacmqniahftxsq63_20260914212119.jpeg)
   [thinking] 第13个接口已选中： - **接口名称**: 深圳海港口岸集装箱吞吐量 - **请求地址**: https://opendata.sz.gov.cn/api/29200_51400003/1/service.xhtml 继续选择第14个接口。
   left_click → [495,423]
52. ![screenshot_52](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2jycktfl1ahgxyx9hy_20260914212124.jpeg)
   [thinking] The dropdown is open and "深圳海港口岸集装箱吞吐量" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
53. ![screenshot_53](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2k0qmn7azahheg33t8_20260914212128.jpeg)
   [thinking] 第14个接口已选中： - **接口名称**: 深圳口岸进出口货物量 - **请求地址**: https://opendata.sz.gov.cn/api/29200_51400004/1/service.xhtml 继续选择第15个接口。
   left_click → [495,423]
54. ![screenshot_54](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2k2l5s9lzahkdlbhkb_20260914212134.jpeg)
   [thinking] The dropdown is open and "深圳口岸进出口货物量" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
55. ![screenshot_55](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2k5d4dze0ahlzdqjrw_20260914212138.jpeg)
   [thinking] 第15个接口已选中： - **接口名称**: 深圳机场口岸空运货物量 - **请求地址**: https://opendata.sz.gov.cn/api/29200_51400005/1/service.xhtml 继续选择第16个接口。
   left_click → [495,423]
56. ![screenshot_56](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2k74vm0paahmzjxhi1_20260914212143.jpeg)
   [thinking] The dropdown is open and "深圳机场口岸空运货物量" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
57. ![screenshot_57](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2k9m4346sahn7js8sh_20260914212148.jpeg)
   [thinking] 第16个接口已选中： - **接口名称**: 热带气旋数据 - **请求地址**: https://opendata.sz.gov.cn/api/1049994100/1/service.html 继续选择第17个接口。
   left_click → [495,423]
58. ![screenshot_58](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2kc00bp6caho2wjs0n_20260914212154.jpeg)
   [thinking] The dropdown is open and "热带气旋数据" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
59. ![screenshot_59](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2keqxsc78ahpgpwnxg_20260914212159.jpeg)
   [thinking] 第17个接口已选中： - **接口名称**: 能见度探测数据 - **请求地址**: https://opendata.sz.gov.cn/api/1580455476/1/service.html 继续选择第18个接口。
   left_click → [495,423]
60. ![screenshot_60](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2kgm6t7zhahsgwuaxw_20260914212204.jpeg)
   [thinking] The dropdown is open and "能见度探测数据" is highlighted. Let me press ArrowDown+Enter to select the next item.
   key → ArrowDown Enter
61. ![screenshot_61](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2kj55fwinahtzu47h3_20260914212208.jpeg)
   [thinking] 第18个接口已选中： - **接口名称**: 预报预警数据_海洋气象 - **请求地址**: https://opendata.sz.gov.cn/api/1464350655/1/service.html 这是我在下拉列表中看到的最后一个接口。根据之前的extract_content结果，下拉列表中只有17个接口。但是任务说大约有47个接口。这意味着可能需要滚动下拉列表才能看到更多接口。 让我检...
   left_click → [495,423]
62. ![screenshot_62](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2klxq996tahuq3r45d_20260914212215.jpeg)
   [thinking] The dropdown is open and "预报预警数据_海洋气象" is highlighted. I can see the last item in the list. Let me try pressing ArrowDown to see if there are more items below.
   key → ArrowDown
63. ![screenshot_63](https://autoglm-agent.aminer.cn/pluginserver/release_1y34zha1000dlf2koae2xshahvrwkbqq_20260914212220.jpeg)
   [final state]
[IMPORTANT] Do NOT proactively open or analyze screenshot links in the steps above. Only when the user requests page screenshots, select relevant ones based on step descriptions and thinking content, then handle accordingly (e.g., download, display).

[result]
按向下键后仍然停留在"预报预警数据_海洋气象"，说明这已经是下拉列表中的最后一个接口了。下拉列表中总共只有18个接口，而不是任务中提到的约47个。

现在我已经收集完了所有18个接口的信息。以下是完整的接口名称与请求地址配对列表：

---

## 深圳市政府数据开放平台 - 接口列表（共18个）

| 序号 | 接口名称 | 请求地址 |
|------|---------|---------|
| 1 | 历史上登陆我国的气旋 | https://opendata.sz.gov.cn/api/29200_00003514/1/service.xhtml |
| 2 | 历年台风的中英文对照表 | https://opendata.sz.gov.cn/api/29200_00003515/1/service.xhtml |
| 3 | 统计月报-物价 | https://opendata.sz.gov.cn/api/29200_03023837/1/service.xhtml |
| 4 | 统计月报-财政金融 | https://opendata.sz.gov.cn/api/29200_03023811/1/service.xhtml |
| 5 | 统计月报-对外贸易 | https://opendata.sz.gov.cn/api/29200_03023797/1/service.xhtml |
| 6 | 统计月报-运输 | https://opendata.sz.gov.cn/api/29200_03023771/1/service.xhtml |
| 7 | 统计月报-固定资产投资 | https://opendata.sz.gov.cn/api/29200_03023757/1/service.xhtml |
| 8 | 统计月报-国民经济核算 | https://opendata.sz.gov.cn/api/29200_03023707/1/service.xhtml |
| 9 | 统计快报 | https://opendata.sz.gov.cn/api/29200_03023659/1/service.html |
| 10 | 预报预警数据_灾害性天气预警 | https://opendata.sz.gov.cn/api/589826355/1/service.html |
| 11 | 二手房成交信息（按日统计） | https://opendata.sz.gov.cn/api/29200_01903517/1/service.xhtml |
| 12 | 一手商品房成交信息（按日统计） | https://opendata.sz.gov.cn/api/29200_01903517/1/service.xhtml |
| 13 | 深圳海港口岸集装箱吞吐量 | https://opendata.sz.gov.cn/api/29200_51400003/1/service.xhtml |
| 14 | 深圳口岸进出口货物量 | https://opendata.sz.gov.cn/api/29200_51400004/1/service.xhtml |
| 15 | 深圳机场口岸空运货物量 | https://opendata.sz.gov.cn/api/29200_51400005/1/service.xhtml |
| 16 | 热带气旋数据 | https://opendata.sz.gov.cn/api/1049994100/1/service.html |
| 17 | 能见度探测数据 | https://opendata.sz.gov.cn/api/1580455476/1/service.html |
| 18 | 预报预警数据_海洋气象 | https://opendata.sz.gov.cn/api/1464350655/1/service.html |

---

**说明**：下拉列表中实际共有18个接口，而非任务中提到的约47个。以上为当前接口选择下拉框中所有可用接口的完整列表。

[session_info]
session_id=cf5cdb2a-5987-4ae1-a338-9841c9ce0fcc
tab_id="243714295"
[tabs]
tabId=243714291 url=chrome-extension://ljlnbmmmgnflklegiafalpieckpihffn/params.html?mcp_ws_domain=ws://127.0.0.1:62030 title=AutoGLM
tabId=243714295 url=https://opendata.sz.gov.cn/maintenance/personal/toApiTest title=深圳市政府数据开放平台个人中心

