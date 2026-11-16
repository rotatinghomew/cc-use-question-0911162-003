人工智能能力建设路径与成果归因平台

运行验收：
python3 -m capability_pathways run --fixture fixtures/acceptance.json --database /tmp/capability_pathways.sqlite3 --output /tmp/capability_pathways-output

核验：
python3 -m capability_pathways verify --database /tmp/capability_pathways.sqlite3 --output /tmp/capability_pathways-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.pathway_signal.test_pathway_feasibility -v

构建检查：
python3 -m compileall -q capability_pathways tests
