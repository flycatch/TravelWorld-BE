from django_elasticsearch_dsl import Document, Index, fields
from .models import State,Country

# Name of the Elasticsearch index
INDEX = Index('states')  # Use a unique index name
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=0,
)


@INDEX.doc_type
class StateDocument(Document):
    country = fields.ObjectField(properties={
        'name': fields.TextField()
    })

    class Django:
        model = State  # The Django model associated with this Document
        fields = [
            'id',
            'name',
        ]
        related_models = [Country]

    def get_queryset(self):
        return super(StateDocument, self).get_queryset().select_related('country')

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Country):
            return related_instance.user_set.all()