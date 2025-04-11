#! /usr/bin/env python

import os

import lab.experiment

import custom_parser
import project
import lab
import sys

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
SCP_LOGIN = "myname@myserver.com"
REMOTE_REPOS_DIR = "/infai/username/projects"
# If REVISION_CACHE is None, the default "./data/revision-cache/" is used.
# REVISION_CACHE = os.environ.get("DOWNWARD_REVISION_CACHE")
if project.REMOTE:
    print("dibo")
    SUITE = project.SUITE_SATISFICING
    ENV = project.BaselSlurmEnvironment(email="my.name@myhost.ch")
else:
    print("vegeta") # ? this is the one that runs
    SUITE = []
    problems = ["depot", "doors", "ferry", "gripper", "hanoi", "miconic"]
    for prob in problems:
        # for idx in range(101):
        for idx in range(99,100):
            # SUITE.append(f"{prob}:with_macros_{str(idx).zfill(3)}.sas")
            SUITE.append(f"{prob}:problem{str(idx).zfill(3)}.sas")
    ENV = project.LocalEnvironment(processes=2)

CONFIGS = [
    ("main", ["--evaluator", "h=goalcount()", "--search", "eager_greedy([h], preferred=[h])"]),
    
    # ("general-macros", ["--evaluator", "h=goalcount()", "--search", "eager_greedy([h], preferred=[h])"]),
    # ("double-open-list", ["--evaluator", "h=goalcount()", "--search", "eager(minol([pgen(h), mgen(h)]))"])
    
    ("general-macros", ["--run_general_macros"]),
    ("double-open-list", ["--run_double_open_list"])
    
    # ("general-macros", []),
    # ("double-open-list", [])
]

# DRIVER_OPTIONS = {
#     "main": [],
#     "general-macros": ["--run_general_macros"],
#     "double-open-list": ["--run_double_open_list"]
# }

ATTRIBUTES = [
    "error",
    # "run_dir",
    "solution_search_time",
    "solution_total_time",
    # "total_time",
    # "h_values",
    "coverage",
    "expansions",
    "memory",
    "macro_search_time",
    "macro_total_time",
    project.EVALUATIONS_PER_TIME,
]

exp = lab.experiment.Experiment(environment=ENV)
problems = {
    "depot": {"Bm": 50000, "Nm": 550},
    "doors": {"Bm": 5000, "Nm": 4000},
    "ferry": {"Bm": 5000, "Nm": 300},
    "gripper": {"Bm": 5000, "Nm": 300},
    "hanoi": {"Bm": 100000, "Nm": 600},
    "miconic": {"Bm": 5000, "Nm": 400}
}
script_dir = "/".join(os.path.dirname(__file__).split("/")[:-1]) + "/"
print(os.path.join(script_dir, "downward-double-open-list/fast-downward.py"))
print(os.path.join(script_dir, f"sas/depot/with_macros_099.sas"))
for prob in problems:
    for idx in range(101):
    # for idx in range(98,99):
        # double open list
        run = exp.add_run()
        run.set_property("domain", prob)
        run.set_property("problem", f"problem{str(idx).zfill(3)}.sas")
        run.set_property("algorithm", "double-open-list")
        run.set_property("id", ["double-open-list", prob, str(idx).zfill(3)])
        run.add_command("learn_macro", [sys.executable, os.path.join(script_dir, "downward-double-open-list/fast-downward.py"), os.path.join(script_dir, f"sas/{prob}/problem{str(idx).zfill(3)}.sas"), "--evaluator", "h=effsize()", "--search", "eager(tiebreaking([sum([g(), h]), h], unsafe_pruning=false), reopen_closed=true, f_eval=sum([g(), h]))", "--search-mode", "macro", "--macro-bm", str(problems[prob]["Bm"]), "--macro-nm", str(problems[prob]["Nm"])])
        run.add_command("translate", [sys.executable, os.path.join(script_dir, "downward-double-open-list/src/translate/custom/macrotxt_to_sas.py"), "-m", f"saved_macros.txt", "-s", os.path.join(script_dir, f"sas/{prob}/problem{str(idx).zfill(3)}.sas")])
        run.add_command("search_solution", [sys.executable, os.path.join(script_dir, "downward-double-open-list/fast-downward.py"), os.path.join(script_dir, f"sas/{prob}/with_macros_{str(idx).zfill(3)}.sas"), "--evaluator", "h=goalcount()", "--search", "eager(minol([pgen(h), mgen(h)]))"])

        # general macros
        run = exp.add_run()
        run.set_property("domain", prob)
        run.set_property("problem", f"problem{str(idx).zfill(3)}.sas")
        run.set_property("algorithm", "general-macros")
        run.set_property("id", ["general-macros", prob, str(idx).zfill(3)])
        run.add_command("learn_macro", [sys.executable, os.path.join(script_dir, "downward-general-macros/fast-downward.py"), os.path.join(script_dir, f"sas/{prob}/problem{str(idx).zfill(3)}.sas"), "--evaluator", "h=effsize()", "--search", "eager(tiebreaking([sum([g(), h]), h], unsafe_pruning=false), reopen_closed=true, f_eval=sum([g(), h]))", "--search-mode", "macro", "--macro-bm", str(problems[prob]["Bm"]), "--macro-nm", str(problems[prob]["Nm"])])
        run.add_command("translate", [sys.executable, os.path.join(script_dir, "downward-general-macros/src/translate/custom/macrotxt_to_sas.py"), "-m", f"saved_macros.txt", "-s", os.path.join(script_dir, f"sas/{prob}/problem{str(idx).zfill(3)}.sas")])
        run.add_command("search_solution", [sys.executable, os.path.join(script_dir, "downward-general-macros/fast-downward.py"), os.path.join(script_dir, f"sas/{prob}/with_macros_{str(idx).zfill(3)}.sas"), "--evaluator", "h=goalcount()", "--search", "eager_greedy([h], preferred=[h])"])

        # no macros
        run = exp.add_run()
        run.set_property("domain", prob)
        run.set_property("problem", f"problem{str(idx).zfill(3)}.sas")
        run.set_property("algorithm", "no-macros")
        run.set_property("id", ["no-macros", prob, str(idx).zfill(3)])
        run.add_command("placeholder_macro_s", [sys.executable, "-c", "print('[t=0s, 0 KB] Macro learning search time: 0s')"])
        run.add_command("placeholder_macro_t", [sys.executable, "-c", "print('[t=0s, 0 KB] Macro learning total time: 0s')"])
        run.add_command("search_solution", [sys.executable, os.path.join(script_dir, "downward-no-macros/fast-downward.py"), os.path.join(script_dir, f"sas/{prob}/problem{str(idx).zfill(3)}.sas"), "--evaluator", "h=goalcount()", "--search", "eager_greedy([h], preferred=[h])"])

# exp.add_parser(project.FastDownwardExperiment.EXITCODE_PARSER)
# exp.add_parser(project.FastDownwardExperiment.TRANSLATOR_PARSER)
exp.add_parser(project.FastDownwardExperiment.SINGLE_SEARCH_PARSER)
exp.add_parser(custom_parser.get_parser())
# exp.add_parser(project.FastDownwardExperiment.PLANNER_PARSER)

exp.add_step("build", exp.build)
exp.add_step("start", exp.start_runs)
exp.add_step("parse", exp.parse)
exp.add_fetcher(name="fetch")

project.add_absolute_report(
    exp, attributes=ATTRIBUTES, filter=[project.add_evaluations_per_time]
)

if not project.REMOTE:
    project.add_scp_step(exp, SCP_LOGIN, REMOTE_REPOS_DIR)

attributes = ["expansions"]
pairs = [
    ("general-macros", "double-open-list"),
]
suffix = "-rel" if project.RELATIVE else ""
for algo1, algo2 in pairs:
    for attr in attributes:
        exp.add_report(
            project.ScatterPlotReport(
                relative=project.RELATIVE,
                get_category=None if project.TEX else lambda run1, run2: run1["domain"],
                attributes=[attr],
                filter_algorithm=[algo1, algo2],
                filter=[project.add_evaluations_per_time],
                format="tex" if project.TEX else "png",
            ),
            name=f"{exp.name}-{algo1}-vs-{algo2}-{attr}{suffix}",
        )

project.add_compress_exp_dir_step(exp)

exp.run_steps()
