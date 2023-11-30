import math

def test(birth_rate : float, max_servers : int, service_rate : float):
    """Simluate a 16 server MMCC queue where the call duration lasts
    an expoential average of 100s."""
    print(loss_rate(birth_rate, service_rate, max_servers))

def get_spec_birth_rate(br : float, servers_empty : int) -> float:
    if servers_empty:
        return br
    return 0.0
    
def get_spec_death_rate(service_rate : float, servers_filled : int, max_servers : int) -> float:
    if servers_filled > max_servers:
        return 0.0
    return service_rate * servers_filled

def find_p_nought(br : float, sr : float, max_servers : int) -> float:
    inverse = 0
    for k in range(max_servers + 1):
        temp = (br / sr)
        temp = temp ** k
        temp = temp / math.factorial(k)
        inverse += temp
    return 1/inverse

def find_p_k(br : float, sr : float, k : int, p_nought : float):
    temp = (br / sr) ** k
    temp = temp / math.factorial(k)
    return p_nought * temp

def loss_rate(br : float, sr: float, max_servers : int) -> float:

    numerator = (br/sr) ** max_servers / math.factorial(max_servers)
    denominator = 0
    for k in range(max_servers + 1):
        temp = (br/sr) ** k
        temp = temp / math.factorial(k)
        denominator += temp

    return numerator / denominator

if __name__ == '__main__':
    test(0.1, 16, 0.01)
