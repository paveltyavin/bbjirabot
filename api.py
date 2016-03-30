from jira import JIRA
import settings


class Api(object):
    versions = None

    def __init__(self):
        self.j = JIRA(
            server=settings.JIRA_URL,
            basic_auth=(settings.JIRA_USERNAME, settings.JIRA_PASSWORD),
        )
        self.project = self.j.project(settings.JIRA_PROJECT)

    def get_versions(self):
        return self.j.project_versions(self.project)

    def get_issues(self, version_name, username):
        if self.versions is None:
            self.versions = self.get_versions()

        version = next(
            (v for v in self.versions
             if version_name in v.name
             and '1C' not in v.name
             and '1С' not in v.name
             and 'WWW' not in v.name
             ), None
        )
        if version is None:
            return []
        else:
            jql = 'project=VIP ' \
                  'AND resolution=Unresolved ' \
                  'AND fixVersion="{fixVersion}"' \
                  'AND assignee in ({assignee})'.format(
                fixVersion=version.name,
                assignee=username,
            )
            return self.j.search_issues(jql)