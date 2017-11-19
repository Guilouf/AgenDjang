import sys
from rest_framework import serializers


module = sys.modules['agendjang.models']


def meta_serializer(name, bases, dct):
    bases += serializers.ModelSerializer,  # append the base class tuple

    class Meta:
        model = getattr(module, name)
        fields = '__all__'

    dct = dict(dct, **{Meta.__name__: Meta})  # merge of the dicts

    return type(f"{name}Serializer", bases, dct)


SERIALIZERS = ['Task', 'DateRange']  # edit to create new serializers

# set the new var
for serial in SERIALIZERS:  # pas reussi a faire plus classe en intention, c'est plus moche en fait
    globals()[f'{serial}Serializer'] = meta_serializer(serial, (), {})
