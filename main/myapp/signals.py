# # signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import ScoreColumn, ResultLearning
#
# is_handling_score_column_creation = False
#
# @receiver(post_save, sender=ScoreColumn)
# def add_score_column_to_all_result_learning(sender, instance, created, **kwargs):
#     global is_handling_score_column_creation
#     if created and not is_handling_score_column_creation:
#         is_handling_score_column_creation = True
#         # Lấy ID của ResultLearning gốc mà từ đó ScoreColumn mới được tạo
#         original_result_learning_id = instance.result_learning.id
#
#         result_learnings = ResultLearning.objects.filter(study_class=instance.result_learning.study_class)
#
#         for result_learning in result_learnings:
#             # Bỏ qua ResultLearning gốc để tránh tạo thêm ScoreColumn không mong muốn
#             if result_learning.id != original_result_learningccd miabn_id:
#                 ScoreColumn.objects.create(
#                     name_column=instance.name_column,
#                     score=0,  # Giá trị mặc định
#                     result_learning=result_learning
#                 )
#
#         is_handling_score_column_creation = False