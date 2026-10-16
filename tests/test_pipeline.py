from job_agent.config import load_config
from job_agent.filters import classify_tab, keep
from job_agent.main import select
from job_agent.models import Job, strip_html
from job_agent.scoring import resume_skills, score

CFG = load_config()
EM, IC = "Engineering Manager", "Senior Engineer & TL"
RESUME = (
    "Senior Engineering Manager, data center networking, distributed systems, Kubernetes, "
    "C/C++, Python, Linux, VXLAN, telemetry, mentoring, release planning"
)


def job(**kw):
    base = dict(source="test", company="Stripe", title="Engineering Manager, Networking",
                location="San Francisco, CA", url="https://x/1",
                description="Lead a team building distributed systems and networking on Kubernetes with Python.")
    base.update(kw)
    return Job(**base)


def test_titles_go_to_the_right_tab():
    assert classify_tab("Engineering Manager, Infrastructure", CFG) == EM
    assert classify_tab("Senior Manager, Software Engineering", CFG) == EM
    assert classify_tab("Director of Engineering", CFG) == EM
    assert classify_tab("Staff Software Engineer, Networking", CFG) == IC
    assert classify_tab("Principal Engineer", CFG) == IC
    assert classify_tab("Tech Lead, Platform", CFG) == IC


def test_unwanted_titles_are_dropped():
    for title in ["Software Engineer", "Senior Solutions Engineer", "Engineering Manager Intern",
                  "Senior Product Manager", "Staff Sales Engineer", "Recruiter, Engineering"]:
        assert classify_tab(title, CFG) is None, title


def test_location_rules():
    assert keep(job(location="Sunnyvale, CA"), CFG)
    assert keep(job(location="Remote - US"), CFG)
    assert keep(job(location="Seattle, WA", remote=True), CFG)
    assert not keep(job(location="Seattle, WA"), CFG)
    assert not keep(job(location="Remote - UK"), CFG)
    assert not keep(job(location="London; Remote"), CFG)


def test_clearance_roles_are_skipped():
    assert not keep(job(description="Active TS/SCI clearance required."), CFG)
    assert not keep(job(description="Must be a U.S. citizen."), CFG)


def test_score_rewards_fit_and_target_companies():
    terms = resume_skills(RESUME, CFG)
    strong = score(job(), terms, CFG)
    weak = score(job(company="Acme", title="Engineering Manager",
                     description="Own payroll, Salesforce CRM integrations and Excel reporting."), terms, CFG)
    assert 0 <= weak < strong <= 100
    assert strong >= 60


def test_cpp_is_matched_as_a_skill():
    assert "c++" in resume_skills("Expert in C++ and Python", CFG)
    assert "c++" not in resume_skills("Experience with C and Python", CFG)


def test_select_skips_already_logged_and_duplicates_and_caps():
    terms = resume_skills(RESUME, CFG)
    jobs = [job(url=f"https://x/{i}", title=f"Engineering Manager, Networking {i}") for i in range(10)]
    jobs.append(job(url="https://x/0-dup", title="Engineering Manager, Networking 0"))  # cross-source dup
    seen = {EM: {"https://x/1"}}
    picked = select(jobs, seen, terms, CFG)
    urls = [j.url for j in picked[EM]]
    assert len(urls) == CFG["max_per_tab"]
    assert "https://x/1" not in urls
    titles = [j.title for j in picked[EM]]
    assert len(titles) == len(set(titles))
    assert picked[IC] == []


def test_strip_html_handles_double_escaped_greenhouse_content():
    assert strip_html("&lt;h2&gt;Who &amp;amp; we are&lt;/h2&gt;") == "Who & we are"
