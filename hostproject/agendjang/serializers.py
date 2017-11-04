import sys
from rest_framework import serializers

# from agendjang.models import Task


# class SerializerLoaderMixin:
#     module = sys.modules[__name__]  # get the current module
#     # fixme c'est sur la classe meta en plus que je dois surcharger.. dc je doit chopper la classe mere de la fille..
#     # fixme surcharger la metaclasse ?
#
#     def __init__(self):
#         self.child_name = self.__class__.__name__
#         self.model_name = self.child_name
#         model = getattr(self.module, self.model_name)  # fixme does not work in lazy




# class TaskSerializer(SerializerLoaderMixin, serializers.ModelSerializer):
#     class Meta:
#         model = Task
#         fields = '__all__'

    # def __str__(self):
    #     return "bite"



# print(TaskSerializer().child_name)

# inst = SerializerLoaderMixin()

# print(inst.model())








# module = sys.modules[__name__]  # module actuel
print(__name__)
module = sys.modules['agendjang.models']
def meta_serializer(name, bases, dct):
    bases += serializers.ModelSerializer,  # append the base class tuple

    class Meta:
        model = getattr(module, name)
        fields = '__all__'

    dct = dict(dct, **{Meta.__name__: Meta})  # merge of the dicts

    return type(f"{name}Serializer", bases, dct)

ClaTaskSer = meta_serializer('Task', (), {})
print(ClaTaskSer.__name__)
print(ClaTaskSer.Meta.__name__)

TaskSerializer = meta_serializer('Task', (), {})

# fixme et pk t'arrive pas a importer??

# class Task(metaclass=meta_serializer):
#     pass
#
# print(Task.__name__)