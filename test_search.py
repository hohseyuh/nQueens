# Run with: python -m unittest -v

import unittest
from main import queens
from search import actions, result, isGoal, pathCost, safe, bfs, dfs
from state_graph import buildGraph, kind

KNOWN = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92}


def valid(state):
    return all(safe(state[:r], c) for r, c in enumerate(state))


class TestTransitions(unittest.TestCase):
    def testInitialActionsAreEveryColumn(self):
        self.assertEqual(actions(4, ()), [0, 1, 2, 3])

    def testActionsSkipAttackedColumns(self):
        # Queen at (0,0) attacks column 0 and diagonal square (1,1) in row 1.
        self.assertEqual(actions(4, (0,)), [2, 3])

    def testDeadEndHasNoActions(self):
        self.assertEqual(actions(4, (0, 2)), [])

    def testResultAppendsColumn(self):
        self.assertEqual(result((1, 3), 0), (1, 3, 0))

    def testGoalTest(self):
        self.assertTrue(isGoal(4, (1, 3, 0, 2)))
        self.assertFalse(isGoal(4, (1, 3, 0)))

    def testPathCostIsNumberOfQueens(self):
        self.assertEqual(pathCost((1, 3, 0, 2)), 4)


class TestSearch(unittest.TestCase):
    def testBothFindAValidGoal(self):
        for n in (1, 4, 5, 6, 8):
            for algo in (bfs, dfs):
                g = algo(n)["goals"][0]
                self.assertEqual(len(g), n)
                self.assertTrue(valid(g), f"{algo.__name__} n={n} gave {g}")

    def testNoSolutionCases(self):
        for n in (2, 3):
            self.assertEqual(bfs(n)["goals"], [])
            self.assertEqual(dfs(n)["goals"], [])

    def testFindAllMatchesKnownCounts(self):
        for n, count in KNOWN.items():
            self.assertEqual(len(dfs(n, True)["goals"]), count)
            self.assertEqual(len(bfs(n, True)["goals"]), count)
            self.assertEqual(queens(n)[0], count)

    def testBfsAndDfsFindTheSameGoalSet(self):
        self.assertEqual(sorted(bfs(6, True)["goals"]), sorted(dfs(6, True)["goals"]))

    def testDfsExpandsFewerNodesForFirstGoal(self):
        self.assertLess(len(dfs(8)["order"]), len(bfs(8)["order"]))
        self.assertLess(dfs(8)["peak"], bfs(8)["peak"])

    def testDfsOrderOn4Queens(self):
        self.assertEqual(dfs(4)["order"], [(), (0,), (0, 2), (0, 3), (0, 3, 1), (1,), (1, 3), (1, 3, 0), (1, 3, 0, 2)])


class TestStateGraph(unittest.TestCase):
    def test4QueensGraph(self):
        g = buildGraph(4)
        self.assertEqual(len(g), 17)
        self.assertEqual(sum(len(v) for v in g.values()), 16)
        self.assertEqual([s for s in g if kind(4, g, s) == "goal"], [(1, 3, 0, 2), (2, 0, 3, 1)])
        self.assertEqual(len([s for s in g if kind(4, g, s) == "dead"]), 4)

    def testEveryEdgeCostsOne(self):
        for children in buildGraph(5).values():
            self.assertTrue(all(w == 1 for _, w in children))


if __name__ == "__main__":
    unittest.main()
