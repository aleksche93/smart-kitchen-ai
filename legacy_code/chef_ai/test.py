from fsm import ChefFSM, ChefTrigger

chef = ChefFSM()

print("\nСимуляція повернення з OFFLINE:")

# Доводимо шефа до OFFLINE
chef.trigger(ChefTrigger.TOXICITY)
chef.trigger(ChefTrigger.INSULT)
chef.trigger(ChefTrigger.TOXICITY)
chef.trigger(ChefTrigger.INSULT)

print("Стан після образ:", chef.state)

# Охолодження
for i in range(5):
    chef.recover()
    print("Крок охолодження:", chef.state, "-", chef.get_behavior())

chef = ChefFSM(profile="chaotic_genius")


chef.trigger(ChefTrigger.HUMOR)
print(chef.respond(ChefTrigger.HUMOR))

chef.trigger(ChefTrigger.RESPECT)
print(chef.respond(ChefTrigger.RESPECT))

chef.trigger(ChefTrigger.APOLOGY)
print(chef.respond(ChefTrigger.APOLOGY))


chef.trigger(ChefTrigger.HUMOR)
print(chef.respond(ChefTrigger.HUMOR))

chef.trigger(ChefTrigger.COMPLEX_TASK)
print(chef.respond(ChefTrigger.COMPLEX_TASK))
