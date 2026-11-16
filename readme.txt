人工智能能力建设路径与成果归因平台

运行验收：
python3 -m capability_pathways run --fixture fixtures/acceptance.json --database /tmp/capability_pathways.sqlite3 --output /tmp/capability_pathways-output

核验：
python3 -m capability_pathways verify --database /tmp/capability_pathways.sqlite3 --output /tmp/capability_pathways-output

分期扩容比较（含已完成、等待资源与已退出机构）：
python3 -m capability_pathways run --fixture fixtures/staged_expansion.json --database /tmp/staged.sqlite3 --output /tmp/staged-output --slots 2

重新比较并生成扩容建议（不重放整批数据）：
python3 -m capability_pathways compare --database /tmp/staged.sqlite3 --output /tmp/staged-compare.json --slots 2

调整资源可用性（名额、导师/算力下限），未完成判断会随之为失效并重新给出建议：
python3 -m capability_pathways resources --database /tmp/staged.sqlite3 --slots 1 --mentor-floor 0.5

更正机构画像（版本递增，旧扩容判断标记为失效后重算）：
python3 -m capability_pathways correct --database /tmp/staged.sqlite3 --record stage-cohort-a-01 --set baseline_level=55.0 --set measured_at=2026-07-01T00:00:00+00:00

查看 / 采纳 / 撤回扩容计划（仅最新草稿可采纳）：
python3 -m capability_pathways plan list --database /tmp/staged.sqlite3
python3 -m capability_pathways plan adopt --database /tmp/staged.sqlite3 --plan-id <plan_id>
python3 -m capability_pathways plan withdraw --database /tmp/staged.sqlite3 --plan-id <plan_id>

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.pathway_signal.test_pathway_feasibility -v
python3 -m unittest tests.measurement.test_staged_comparison -v

构建检查：
python3 -m compileall -q capability_pathways tests
