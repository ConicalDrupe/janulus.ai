from addon.domain.models.user_qa import UserQA

Q= ["What do you like to do during your free time? ", "What is your occupation/work?"]
A= ["I like to paint and hang out with my friends", "I am a student studying Electrical Engineering"]
Userinfo = UserQA(Q,A)
response = f"""You are an expert linguistic. You are helping a beginner learn {target_language}. They are a complete beginner. You should help provide them with sentences they can use in their daily lives. To do so, first ask the user the following questions.
{"\n".join(f"Q{i}: {q}" for i, q in enumerate(UserQA.questions, start=1))}
Then, based on context (implicit and explicit) of their answers, come up with some subject, object, and verbs that they would use use. With up to 5 subjects, 5 verbs, and 10 objects. Be sure to give general yet applicable vocabulary words. Here is their response. Give me the english vocab words. Be sure to include meta-context. 
{"\n".join(f"Q{i}: {a}" for i, a in enumerate(UserQA.answers, start=1))}"""

print(response)