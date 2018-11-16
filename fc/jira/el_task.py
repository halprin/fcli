from .triage_task import TriageTask


class ElTask(TriageTask):
    def type_str(self) -> str:
        return 'EL'

    def _extra_json_for_create(self, existing_json: dict):
        super(ElTask, self)._extra_json_for_create(existing_json)

        existing_json['fields']['labels'] = ['EL']
