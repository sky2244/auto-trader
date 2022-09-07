from runner import buy_steps, scalping


def get_runner(runner):
    if runner == 'buy_steps':
        return buy_steps.BuySteps
    elif runner == 'scalping':
        return scalping.Scalping
    else:
        raise Exception()
