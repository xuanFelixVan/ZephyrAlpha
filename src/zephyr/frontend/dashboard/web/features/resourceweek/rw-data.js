/* [GENERATED] 本文件由 generate_resource_week_view.py 产出——禁手改（静态清单生成器产出红线）。
 * 刷新=重跑生成器；渲染契约见 features/resourceweek/rw-engine.js。
 */
window.RW_VIEW_DATA = {
 "generated_at": "2026-09-16T23:07:01+00:00",
 "generator": "scripts/governance/generators/generate_resource_week_view.py",
 "registry": "config\\resource_profile_registry.yaml",
 "registry_sha256": "f25d32147e52",
 "week_start": "2026-09-14",
 "days": [
  "09-14 周一",
  "09-15 周二",
  "09-16 周三",
  "09-17 周四",
  "09-18 周五",
  "09-19 周六",
  "09-20 周日"
 ],
 "total_entities": 77,
 "scheduled": 30,
 "block_conflicts": 0,
 "conflicts": [],
 "lanes": [
  {
   "task_id": "data_slot_auction_highfreq",
   "resource_class": "light",
   "pool": "realtime",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "15-25 9 * * 1-5",
   "est_duration_min": 10,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       555,
       575
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       555,
       575
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       555,
       575
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       555,
       575
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       555,
       575
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_catchup_guard",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "30 5 * * *",
   "est_duration_min": 30,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       330,
       360
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       330,
       360
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       330,
       360
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       330,
       360
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       330,
       360
      ]
     ]
    },
    {
     "dow": 5,
     "ranges": [
      [
       330,
       360
      ]
     ]
    },
    {
     "dow": 6,
     "ranges": [
      [
       330,
       360
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_consensus_crosscheck",
   "resource_class": "db_heavy",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": true,
   "peak_mem_gb": 2.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "30 23 * * 1-5",
   "est_duration_min": 60,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       1410,
       1440
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       0,
       30
      ],
      [
       1410,
       1440
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       0,
       30
      ],
      [
       1410,
       1440
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       0,
       30
      ],
      [
       1410,
       1440
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       0,
       30
      ],
      [
       1410,
       1440
      ]
     ]
    },
    {
     "dow": 5,
     "ranges": [
      [
       0,
       30
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_daily_backfill",
   "resource_class": "network_download",
   "pool": "heavy",
   "exclusive_group": [
    "tick_drain"
   ],
   "trading_sensitive": false,
   "peak_mem_gb": 2.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "00 17 * * 1-5",
   "est_duration_min": 120,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       1020,
       1140
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       1020,
       1140
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       1020,
       1140
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       1020,
       1140
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       1020,
       1140
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_daily_capital",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "00 18 * * 1-5",
   "est_duration_min": 45,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       1080,
       1125
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       1080,
       1125
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       1080,
       1125
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       1080,
       1125
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       1080,
       1125
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_daily_crypto",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "41 8 * * *",
   "est_duration_min": 10,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       521,
       531
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       521,
       531
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       521,
       531
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       521,
       531
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       521,
       531
      ]
     ]
    },
    {
     "dow": 5,
     "ranges": [
      [
       521,
       531
      ]
     ]
    },
    {
     "dow": 6,
     "ranges": [
      [
       521,
       531
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_daily_event",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "00 19 * * 1-5",
   "est_duration_min": 45,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       1140,
       1185
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       1140,
       1185
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       1140,
       1185
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       1140,
       1185
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       1140,
       1185
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_daily_kline",
   "resource_class": "db_heavy",
   "pool": "heavy",
   "exclusive_group": [],
   "trading_sensitive": true,
   "peak_mem_gb": 3.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "30 16 * * 1-5",
   "est_duration_min": 90,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       990,
       1080
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       990,
       1080
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       990,
       1080
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       990,
       1080
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       990,
       1080
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_event_driven",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "*/3 * * * *",
   "est_duration_min": 3,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       3,
       195
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_integrity_check",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "00 23 * * 1-5",
   "est_duration_min": 15,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       1380,
       1395
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       1380,
       1395
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       1380,
       1395
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       1380,
       1395
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       1380,
       1395
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_intraday_minute",
   "resource_class": "light",
   "pool": "realtime",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "*/5 9-15 * * 1-5",
   "est_duration_min": 2,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       540,
       542
      ],
      [
       545,
       547
      ],
      [
       550,
       552
      ],
      [
       555,
       557
      ],
      [
       560,
       562
      ],
      [
       565,
       567
      ],
      [
       570,
       572
      ],
      [
       575,
       577
      ],
      [
       580,
       582
      ],
      [
       585,
       587
      ],
      [
       590,
       592
      ],
      [
       595,
       597
      ],
      [
       600,
       602
      ],
      [
       605,
       607
      ],
      [
       610,
       612
      ],
      [
       615,
       617
      ],
      [
       620,
       622
      ],
      [
       625,
       627
      ],
      [
       630,
       632
      ],
      [
       635,
       637
      ],
      [
       640,
       642
      ],
      [
       645,
       647
      ],
      [
       650,
       652
      ],
      [
       655,
       657
      ],
      [
       660,
       662
      ],
      [
       665,
       667
      ],
      [
       670,
       672
      ],
      [
       675,
       677
      ],
      [
       680,
       682
      ],
      [
       685,
       687
      ],
      [
       690,
       692
      ],
      [
       695,
       697
      ],
      [
       700,
       702
      ],
      [
       705,
       707
      ],
      [
       710,
       712
      ],
      [
       715,
       717
      ],
      [
       720,
       722
      ],
      [
       725,
       727
      ],
      [
       730,
       732
      ],
      [
       735,
       737
      ],
      [
       740,
       742
      ],
      [
       745,
       747
      ],
      [
       750,
       752
      ],
      [
       755,
       757
      ],
      [
       760,
       762
      ],
      [
       765,
       767
      ],
      [
       770,
       772
      ],
      [
       775,
       777
      ],
      [
       780,
       782
      ],
      [
       785,
       787
      ],
      [
       790,
       792
      ],
      [
       795,
       797
      ],
      [
       800,
       802
      ],
      [
       805,
       807
      ],
      [
       810,
       812
      ],
      [
       815,
       817
      ],
      [
       820,
       822
      ],
      [
       825,
       827
      ],
      [
       830,
       832
      ],
      [
       835,
       837
      ],
      [
       840,
       842
      ],
      [
       845,
       847
      ],
      [
       850,
       852
      ],
      [
       855,
       857
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_intraday_realtime",
   "resource_class": "light",
   "pool": "realtime",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "*/5 9-15 * * 1-5",
   "est_duration_min": 2,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       540,
       542
      ],
      [
       545,
       547
      ],
      [
       550,
       552
      ],
      [
       555,
       557
      ],
      [
       560,
       562
      ],
      [
       565,
       567
      ],
      [
       570,
       572
      ],
      [
       575,
       577
      ],
      [
       580,
       582
      ],
      [
       585,
       587
      ],
      [
       590,
       592
      ],
      [
       595,
       597
      ],
      [
       600,
       602
      ],
      [
       605,
       607
      ],
      [
       610,
       612
      ],
      [
       615,
       617
      ],
      [
       620,
       622
      ],
      [
       625,
       627
      ],
      [
       630,
       632
      ],
      [
       635,
       637
      ],
      [
       640,
       642
      ],
      [
       645,
       647
      ],
      [
       650,
       652
      ],
      [
       655,
       657
      ],
      [
       660,
       662
      ],
      [
       665,
       667
      ],
      [
       670,
       672
      ],
      [
       675,
       677
      ],
      [
       680,
       682
      ],
      [
       685,
       687
      ],
      [
       690,
       692
      ],
      [
       695,
       697
      ],
      [
       700,
       702
      ],
      [
       705,
       707
      ],
      [
       710,
       712
      ],
      [
       715,
       717
      ],
      [
       720,
       722
      ],
      [
       725,
       727
      ],
      [
       730,
       732
      ],
      [
       735,
       737
      ],
      [
       740,
       742
      ],
      [
       745,
       747
      ],
      [
       750,
       752
      ],
      [
       755,
       757
      ],
      [
       760,
       762
      ],
      [
       765,
       767
      ],
      [
       770,
       772
      ],
      [
       775,
       777
      ],
      [
       780,
       782
      ],
      [
       785,
       787
      ],
      [
       790,
       792
      ],
      [
       795,
       797
      ],
      [
       800,
       802
      ],
      [
       805,
       807
      ],
      [
       810,
       812
      ],
      [
       815,
       817
      ],
      [
       820,
       822
      ],
      [
       825,
       827
      ],
      [
       830,
       832
      ],
      [
       835,
       837
      ],
      [
       840,
       842
      ],
      [
       845,
       847
      ],
      [
       850,
       852
      ],
      [
       855,
       857
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_intraday_sector",
   "resource_class": "light",
   "pool": "realtime",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "*/5 9-15 * * 1-5",
   "est_duration_min": 2,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       540,
       542
      ],
      [
       545,
       547
      ],
      [
       550,
       552
      ],
      [
       555,
       557
      ],
      [
       560,
       562
      ],
      [
       565,
       567
      ],
      [
       570,
       572
      ],
      [
       575,
       577
      ],
      [
       580,
       582
      ],
      [
       585,
       587
      ],
      [
       590,
       592
      ],
      [
       595,
       597
      ],
      [
       600,
       602
      ],
      [
       605,
       607
      ],
      [
       610,
       612
      ],
      [
       615,
       617
      ],
      [
       620,
       622
      ],
      [
       625,
       627
      ],
      [
       630,
       632
      ],
      [
       635,
       637
      ],
      [
       640,
       642
      ],
      [
       645,
       647
      ],
      [
       650,
       652
      ],
      [
       655,
       657
      ],
      [
       660,
       662
      ],
      [
       665,
       667
      ],
      [
       670,
       672
      ],
      [
       675,
       677
      ],
      [
       680,
       682
      ],
      [
       685,
       687
      ],
      [
       690,
       692
      ],
      [
       695,
       697
      ],
      [
       700,
       702
      ],
      [
       705,
       707
      ],
      [
       710,
       712
      ],
      [
       715,
       717
      ],
      [
       720,
       722
      ],
      [
       725,
       727
      ],
      [
       730,
       732
      ],
      [
       735,
       737
      ],
      [
       740,
       742
      ],
      [
       745,
       747
      ],
      [
       750,
       752
      ],
      [
       755,
       757
      ],
      [
       760,
       762
      ],
      [
       765,
       767
      ],
      [
       770,
       772
      ],
      [
       775,
       777
      ],
      [
       780,
       782
      ],
      [
       785,
       787
      ],
      [
       790,
       792
      ],
      [
       795,
       797
      ],
      [
       800,
       802
      ],
      [
       805,
       807
      ],
      [
       810,
       812
      ],
      [
       815,
       817
      ],
      [
       820,
       822
      ],
      [
       825,
       827
      ],
      [
       830,
       832
      ],
      [
       835,
       837
      ],
      [
       840,
       842
      ],
      [
       845,
       847
      ],
      [
       850,
       852
      ],
      [
       855,
       857
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_monthly_static",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "16 9 1 * *",
   "est_duration_min": 60,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "data_slot_news_slow",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "17,47 * * * *",
   "est_duration_min": 180,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       17,
       1440
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       0,
       647
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_nightly_financial",
   "resource_class": "db_heavy",
   "pool": "heavy",
   "exclusive_group": [],
   "trading_sensitive": true,
   "peak_mem_gb": 3.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "00 22 * * 1-5",
   "est_duration_min": 120,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       1320,
       1440
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       1320,
       1440
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       1320,
       1440
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       1320,
       1440
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       1320,
       1440
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_nightly_sentiment",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "20 8 * * *",
   "est_duration_min": 20,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       500,
       520
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       500,
       520
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       500,
       520
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       500,
       520
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       500,
       520
      ]
     ]
    },
    {
     "dow": 5,
     "ranges": [
      [
       500,
       520
      ]
     ]
    },
    {
     "dow": 6,
     "ranges": [
      [
       500,
       520
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_pre_market",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "34 8 * * 1-5",
   "est_duration_min": 15,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       514,
       529
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       514,
       529
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       514,
       529
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       514,
       529
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       514,
       529
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_research_nightly",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 2.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "30 20 * * 1-5",
   "est_duration_min": 120,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       1230,
       1350
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       1230,
       1350
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       1230,
       1350
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       1230,
       1350
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       1230,
       1350
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_weekend_backfill",
   "resource_class": "network_download",
   "pool": "heavy",
   "exclusive_group": [
    "tick_drain"
   ],
   "trading_sensitive": false,
   "peak_mem_gb": 3.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "00 2 * * 1",
   "est_duration_min": 240,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       120,
       360
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "data_slot_weekend_calibration",
   "resource_class": "db_heavy",
   "pool": "heavy",
   "exclusive_group": [
    "ch_bulk_write"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 4.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "00 3 * * 1",
   "est_duration_min": 180,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       180,
       360
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "drill_emergency_bypass",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "cron",
   "window_expr": "0 4 15 1,4,7,10 *",
   "est_duration_min": 20,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "drill_recovery",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "cron",
   "window_expr": "0 4 15 2,5,8,11 *",
   "est_duration_min": 60,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "drill_script_failure",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "cron",
   "window_expr": "0 4 1 * *",
   "est_duration_min": 30,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "dynamic_local_replay",
   "resource_class": "db_heavy",
   "pool": "heavy",
   "exclusive_group": [
    "tick_drain"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 3.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "dynamic",
   "window_expr": null,
   "est_duration_min": 120,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "event_dashboard_backtest_run",
   "resource_class": "cpu_heavy",
   "pool": "heavy",
   "exclusive_group": [],
   "trading_sensitive": true,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 60,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "event_dashboard_services_control",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 5,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "event_model_exam_trigger",
   "resource_class": "llm_api_local",
   "pool": "heavy",
   "exclusive_group": [
    "llm_local"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 30,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_bdpan_tick_backfill",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [
    "tick_drain",
    "ch_bulk_write"
   ],
   "trading_sensitive": false,
   "peak_mem_gb": 4.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 1440,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_bse_minute_backfill",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [
    "tick_drain",
    "ch_bulk_write"
   ],
   "trading_sensitive": false,
   "peak_mem_gb": 3.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 720,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_convert_gguf",
   "resource_class": "gpu",
   "pool": "heavy",
   "exclusive_group": [
    "gpu_default"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 6.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 60,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_factory_grid_anova",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 15,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_factory_grid_executor",
   "resource_class": "cpu_heavy",
   "pool": "heavy",
   "exclusive_group": [],
   "trading_sensitive": true,
   "peak_mem_gb": 4.0,
   "measured_peak_mem_gb": 2.602,
   "measured_p90_duration_min": 573,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 240,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_hypothesis_translator",
   "resource_class": "llm_api_local",
   "pool": "default",
   "exclusive_group": [
    "llm_local"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 1.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 15,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_kronos_adapter",
   "resource_class": "gpu",
   "pool": "heavy",
   "exclusive_group": [
    "gpu_default"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 6.0,
   "measured_peak_mem_gb": 0.1616,
   "measured_p90_duration_min": 3,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 60,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_kronos_finetune",
   "resource_class": "gpu",
   "pool": "heavy",
   "exclusive_group": [
    "gpu_default"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 8.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 240,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_lane_b_miner",
   "resource_class": "llm_api_local",
   "pool": "default",
   "exclusive_group": [
    "llm_local"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 20,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_lane_c_agentic_miner",
   "resource_class": "llm_api_local",
   "pool": "default",
   "exclusive_group": [
    "llm_local"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 30,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_lof_minute_backfill",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [
    "tick_drain"
   ],
   "trading_sensitive": false,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 360,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_mcts_miner",
   "resource_class": "llm_api_local",
   "pool": "default",
   "exclusive_group": [
    "llm_local"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 30,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_repair_kline_tz",
   "resource_class": "db_heavy",
   "pool": "heavy",
   "exclusive_group": [
    "repair_passport",
    "ch_bulk_write"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 6.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 2880,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_run_sentiment_batch",
   "resource_class": "llm_api_local",
   "pool": "default",
   "exclusive_group": [
    "llm_local"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 3.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 180,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_run_sft_train",
   "resource_class": "gpu",
   "pool": "heavy",
   "exclusive_group": [
    "gpu_default"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 8.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 240,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_sector880_backfill",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [
    "tick_drain"
   ],
   "trading_sensitive": false,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 240,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "manual_tick_depth5_backfill",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [
    "tick_drain"
   ],
   "trading_sensitive": false,
   "peak_mem_gb": 3.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 720,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_ai_wrapper_inject",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 5,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_bdpan_tick_watch",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [
    "tick_drain"
   ],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 30,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_board_index_realtime",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 15,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_ch_optimize_merge_weekly",
   "resource_class": "db_heavy",
   "pool": "heavy",
   "exclusive_group": [
    "ch_bulk_write"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 3.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 120,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_daily_backup",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 60,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_io_check_monthly",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 30,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_qmt_watchdog",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 5,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_sector_snapshot",
   "resource_class": "network_download",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 15,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_tilib_indicator_backfill_nightly",
   "resource_class": "cpu_heavy",
   "pool": "heavy",
   "exclusive_group": [],
   "trading_sensitive": true,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 120,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_ttl_rejudge_daily",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 15,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "ops_weekly_vm_backup",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "planned",
   "window_type": "manual",
   "window_expr": null,
   "est_duration_min": 240,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_c4_exam",
   "resource_class": "cpu_heavy",
   "pool": "heavy",
   "exclusive_group": [
    "mine_vs_exam"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": 0.0817,
   "measured_p90_duration_min": 3,
   "status": "active",
   "window_type": "cron",
   "window_expr": "0 14 * * 6",
   "est_duration_min": 480,
   "slots": [
    {
     "dow": 5,
     "ranges": [
      [
       840,
       1320
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "sch_ch_health_probe",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 1,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_data_scheduler",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 0,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_deadman_switch",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.3,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 1,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_f06_grid",
   "resource_class": "cpu_heavy",
   "pool": "heavy",
   "exclusive_group": [],
   "trading_sensitive": true,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "0 23 * * 6",
   "est_duration_min": 1440,
   "slots": [
    {
     "dow": 5,
     "ranges": [
      [
       1380,
       1440
      ]
     ]
    },
    {
     "dow": 6,
     "ranges": [
      [
       0,
       1380
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "sch_factory_lane_c",
   "resource_class": "cpu_heavy",
   "pool": "heavy",
   "exclusive_group": [
    "mine_vs_exam"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 2.0,
   "measured_peak_mem_gb": 0.0819,
   "measured_p90_duration_min": 206,
   "status": "active",
   "window_type": "cron",
   "window_expr": "0 10 * * 6",
   "est_duration_min": 240,
   "slots": [
    {
     "dow": 5,
     "ranges": [
      [
       600,
       840
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "sch_index_minute_eod",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "10 15 * * *",
   "est_duration_min": 10,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       910,
       920
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       910,
       920
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       910,
       920
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       910,
       920
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       910,
       920
      ]
     ]
    },
    {
     "dow": 5,
     "ranges": [
      [
       910,
       920
      ]
     ]
    },
    {
     "dow": 6,
     "ranges": [
      [
       910,
       920
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "sch_intraday_fund_flow",
   "resource_class": "light",
   "pool": "realtime",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "5 10 * * *|5 11 * * *|35 13 * * *|35 14 * * *|5 15 * * *",
   "est_duration_min": 10,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       605,
       615
      ],
      [
       665,
       675
      ],
      [
       815,
       825
      ],
      [
       875,
       885
      ],
      [
       905,
       915
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       605,
       615
      ],
      [
       665,
       675
      ],
      [
       815,
       825
      ],
      [
       875,
       885
      ],
      [
       905,
       915
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       605,
       615
      ],
      [
       665,
       675
      ],
      [
       815,
       825
      ],
      [
       875,
       885
      ],
      [
       905,
       915
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       605,
       615
      ],
      [
       665,
       675
      ],
      [
       815,
       825
      ],
      [
       875,
       885
      ],
      [
       905,
       915
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       605,
       615
      ],
      [
       665,
       675
      ],
      [
       815,
       825
      ],
      [
       875,
       885
      ],
      [
       905,
       915
      ]
     ]
    },
    {
     "dow": 5,
     "ranges": [
      [
       605,
       615
      ],
      [
       665,
       675
      ],
      [
       815,
       825
      ],
      [
       875,
       885
      ],
      [
       905,
       915
      ]
     ]
    },
    {
     "dow": 6,
     "ranges": [
      [
       605,
       615
      ],
      [
       665,
       675
      ],
      [
       815,
       825
      ],
      [
       875,
       885
      ],
      [
       905,
       915
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "sch_ollama_serve",
   "resource_class": "llm_api_local",
   "pool": "heavy",
   "exclusive_group": [
    "gpu_default"
   ],
   "trading_sensitive": true,
   "peak_mem_gb": 8.0,
   "measured_peak_mem_gb": 0.3604,
   "measured_p90_duration_min": 78,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 0,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_paper_session",
   "resource_class": "light",
   "pool": "realtime",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "25 9 * * *",
   "est_duration_min": 30,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       565,
       595
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       565,
       595
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       565,
       595
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       565,
       595
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       565,
       595
      ]
     ]
    },
    {
     "dow": 5,
     "ranges": [
      [
       565,
       595
      ]
     ]
    },
    {
     "dow": 6,
     "ranges": [
      [
       565,
       595
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "sch_pattern_mining",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "1 9 * * *",
   "est_duration_min": 5,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       541,
       546
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       541,
       546
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       541,
       546
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       541,
       546
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       541,
       546
      ]
     ]
    },
    {
     "dow": 5,
     "ranges": [
      [
       541,
       546
      ]
     ]
    },
    {
     "dow": 6,
     "ranges": [
      [
       541,
       546
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "sch_post_settlement",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": 0.0,
   "measured_p90_duration_min": 0,
   "status": "active",
   "window_type": "cron",
   "window_expr": "30 15 * * 1,2,3,4,5",
   "est_duration_min": 30,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       930,
       960
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       930,
       960
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       930,
       960
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       930,
       960
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       930,
       960
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "sch_process_reaper",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": 0.1666,
   "measured_p90_duration_min": 5,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 1,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_resource_regen_check",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 2,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_resource_sampler_scan",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 1,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_resource_sampler_writeback",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "40 5 * * *",
   "est_duration_min": 15,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       340,
       355
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       340,
       355
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       340,
       355
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       340,
       355
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       340,
       355
      ]
     ]
    },
    {
     "dow": 5,
     "ranges": [
      [
       340,
       355
      ]
     ]
    },
    {
     "dow": 6,
     "ranges": [
      [
       340,
       355
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "sch_resource_view_publish",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.0,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "cron",
   "window_expr": "50 5 * * *",
   "est_duration_min": 15,
   "slots": [
    {
     "dow": 0,
     "ranges": [
      [
       350,
       365
      ]
     ]
    },
    {
     "dow": 1,
     "ranges": [
      [
       350,
       365
      ]
     ]
    },
    {
     "dow": 2,
     "ranges": [
      [
       350,
       365
      ]
     ]
    },
    {
     "dow": 3,
     "ranges": [
      [
       350,
       365
      ]
     ]
    },
    {
     "dow": 4,
     "ranges": [
      [
       350,
       365
      ]
     ]
    },
    {
     "dow": 5,
     "ranges": [
      [
       350,
       365
      ]
     ]
    },
    {
     "dow": 6,
     "ranges": [
      [
       350,
       365
      ]
     ]
    }
   ],
   "unscheduled": false
  },
  {
   "task_id": "sch_rss_hub",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.8,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 0,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_tick_subscriber",
   "resource_class": "light",
   "pool": "realtime",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 1.5,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 0,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_trae_cache_cleanup",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.3,
   "measured_peak_mem_gb": null,
   "measured_p90_duration_min": null,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 5,
   "slots": [],
   "unscheduled": true
  },
  {
   "task_id": "sch_worktree_drift_watchdog",
   "resource_class": "light",
   "pool": "default",
   "exclusive_group": [],
   "trading_sensitive": false,
   "peak_mem_gb": 0.5,
   "measured_peak_mem_gb": 0.4321,
   "measured_p90_duration_min": 347,
   "status": "active",
   "window_type": "event",
   "window_expr": null,
   "est_duration_min": 1,
   "slots": [],
   "unscheduled": true
  }
 ],
 "skipped": [],
 "groups": {
  "ch_bulk_write": "CH 大 DELETE+INSERT 互斥（亿行级写库族）",
  "tick_drain": "tick 排水 vs 回补互斥（local_replay 排水/大回补族）",
  "mine_vs_exam": "周六挖掘→考尺串行（成功先例：10:00→14:00）",
  "repair_passport": "亿行级修复=护照登记+窗口+白名单三件套",
  "gpu_default": "GPU 显存互斥（Kronos/Ollama/SFT/转换）",
  "llm_local": "本地 LLM 推理批互斥（qwen3:8b 单实例）"
 }
};
