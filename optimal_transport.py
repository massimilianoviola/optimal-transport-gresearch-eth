import numpy as np


def find_optimal_transport(C, G, P):
    EXP = 25  # tune to increase score
    N = len(C)
    best_transportation_plan = []
    best_profit = 0
    # reproducible baseline solutions + randomization
    perms = [range(N), range(N - 1, -1, -1)] + [np.random.permutation(N) for _ in range(20)]
    C_back = C.copy()

    for perm in perms:
        transportation_plan = []
        for ind_selling in perm:
            # view all available trades, to execute the best ones in order
            profit_per_city = []
            for ind_buying in range(N):
                # get price and amount of commodities that a city wants to buy or sell
                sell_Q = C[ind_selling][3]
                sell_price = C[ind_selling][1]
                buy_Q = C[ind_buying][2]
                buy_price = C[ind_buying][0]
                quant = min(buy_Q, sell_Q)

                if quant > 0:
                    profit = quant * (buy_price - sell_price - G[ind_selling, ind_buying])
                    if profit > 0:
                        # trick: weigh the profit by the (exponentiated) probability that the trade occurs
                        # this quantifies the risk, and larger exponents favor moderately profitable but safer trades
                        profit_per_city += [
                            [ind_buying, profit * (1 - P[ind_selling, ind_buying]) ** EXP]
                        ]

            # sort cities to sell to by this risk-aware profit measure
            profit_per_city.sort(key=lambda x: x[1], reverse=True)

            # while there is supply and demand, sell in order of profitability
            # create optimized transportation plan
            for ind_buying, _ in profit_per_city:
                # print(ind_buying)
                sell_Q = C[ind_selling][3]
                buy_Q = C[ind_buying][2]
                quant = min(buy_Q, sell_Q)
                # update storage of the commodity for both cities
                C[ind_selling][3] = C[ind_selling][3] - quant
                C[ind_buying][2] = C[ind_buying][2] - quant

                transportation_plan += [[ind_selling, ind_buying, quant]]

        total_profit = 0
        # calculate expected profit
        for [ind_selling, ind_buying, quant] in transportation_plan:
            sell_price = C[ind_selling][1]
            buy_price = C[ind_buying][0]
            # now weigh the profit with the real probability that the trade will occur
            total_profit += (
                quant
                * (buy_price - sell_price - G[ind_selling, ind_buying])
                * (1 - P[ind_selling, ind_buying])
            )
        # print(total_profit)

        # update best solution
        if total_profit > best_profit:
            best_profit = total_profit
            best_transportation_plan = transportation_plan

        # restore C, modified in place
        C = C_back.copy()

    return np.array(best_transportation_plan)


if __name__ == "__main__":
    C = np.array(
        [
            [98, 100, 100, 100],
            [98, 100, 100, 100],
            [102, 103, 30, 100],
            [102, 103, 50, 100],
            [101, 103, 50, 100],
        ]
    )

    G = np.array(
        [
            [0, 1, 1, 1, 1],
            [1, 0, 1, 1, 1],
            [1, 1, 0, 1, 1],
            [1, 1, 1, 0, 1],
            [1, 1, 1, 1, 0],
        ]
    )

    P = np.array(
        [
            [0, 0.2, 0.5, 0, 0.5],
            [0.2, 0, 0.5, 0.3, 0],
            [0.5, 0.5, 0, 0, 0.3],
            [0, 0.3, 0, 0, 0],
            [0.5, 0, 0.3, 0, 0],
        ]
    )

    find_optimal_transport(C, G, P)
