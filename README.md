# MPI Programming Project

This project implements a parallel algorithm for a game called “Lord of the Processors: The Two Towers” using the Python MPI library. The cellular automaton model is used in the simulation of complex systems.

## Introduction
The project focuses on parallel programming with Python using the MPI library. The goal is to implement a parallel algorithm for the game “Lord of the Processors: The Two Towers”, which is a combination of battleship and tower defense.

## Cellular Automata
The cellular automaton is a discrete computational model used in the study of complex systems. It is composed of an N-dimensional orthogonal grid called the “map”, and rules of evolution. The system evolves by a set of rules via simulation.

## Lord of the Processors: The Two Towers (LOTP: TTT)
The game is played on a 2-dimensional orthogonal grid (i.e. a matrix) and consists of towers, each with their own health points and attack power. Each tower can attack its neighbors simultaneously, and if a tower’s health drops to 0 or below, it gets destroyed. There are two types of towers: ‘o’ tower and ‘+’ tower. A tower does not attack the same type of tower, with ‘+’ towers attacking ‘o’ towers and ‘o’ towers attacking ‘+’ towers.

## Parallel Simulation of LOTP: TTT
The simulation of the game is done in parallel using Python and the MPI library. The task is divided between one manager process and P worker processes. The manager distributes the simulation task to the workers, and the workers work on the task while occasionally communicating with each other.

## Running
To run a Python code like game.py, use the following command:
```bash
mpiexec -n <P> python game.py input.txt output.txt
```

Where **<P>** is the number of worker processes.

## Game Progression
Initialize the map with empty cells marked with a dot symbol (‘.’).
Iterate for W waves:
a. Place new towers on the map. If there is already a tower at the location where a new tower is to be placed, ignore it.
b. Iterate for 8 rounds:
i. All the towers on the map attack simultaneously.
ii. Reduce each tower’s health points according to the total damage it received.
iii. Destroy the tower and make its location on the map empty ("."), if a tower’s health drops to 0 or below.
Print the final map.
Note: Health points of the towers are carried over to new rounds and new waves. The crucial part of the simulation is keeping track of the health of the towers because health is the only variable that changes between rounds.
