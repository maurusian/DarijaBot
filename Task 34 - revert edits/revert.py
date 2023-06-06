import sys, json, pywikibot
from datetime import datetime, timedelta

def read_json_file(site, json_page_title):
    json_page = pywikibot.Page(site, json_page_title)
    json_content = json_page.get()
    return json.loads(json_content)

def revert_edits(site, user, hours, comment_string, edit_summary):
    now = datetime.utcnow()
    time_limit = now - timedelta(hours=hours)

    user_contribs = pywikibot.User(site, user).contributions(total=None, namespaces=[0], end=time_limit)

    for contrib in user_contribs:
        page = contrib[0]
        timestamp = contrib[1]
        comment = contrib[3]

        if comment_string in comment:
            try:
                revisions = list(page.revisions(total=2, content=False))
                previous_revision = revisions[1] if len(revisions) > 1 else None

                if previous_revision:
                    previous_content = page.getOldVersion(previous_revision.revid)
                    page.put(previous_content, summary=edit_summary, botflag=True)
                    print(f"Reverted edit on {page.title()} at {timestamp}")
                else:
                    print(f"Error: No previous revision found for {page.title()} at {timestamp}")

            except Exception as e:
                print(f"Error reverting edit on {page.title()} at {timestamp}: {e}")

def main():

    site = pywikibot.Site()
    JOB_NUMBER = 1
    json_page_title = f"ميدياويكي:عطاشة34.خدمة{JOB_NUMBER}.json"
    site.login()

    json_data = read_json_file(site, json_page_title)
    user = json_data["user"]
    hours = json_data["hours"]
    comment_string = json_data["comment_string"]
    edit_summary = json_data["edit_summary"]

    revert_edits(site, user, hours, comment_string, edit_summary)

if __name__ == "__main__":
    main()
