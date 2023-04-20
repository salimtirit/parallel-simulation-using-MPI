import sys
import re
import math
import numpy
import sys
from mpi4py import MPI
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    inputName = sys.argv[1]
    outputName = sys.argv[2]
    inputFile = open(inputName, "r")

    all_lines = []

    for line in inputFile:
        line = line.strip()
        if line == "":
            continue
        all_lines.append(line)
    line = list(map(int, all_lines[0].split(" ")))
    N = line[0]  # size
    W = line[1]  # wave
    T = line[2]  # tower
    table = [".0"]*(N**2)
    num_cells = int(N//int(math.sqrt(size-1)))
    for p in range(1, size):
        comm.send(N, dest=p, tag=10)
        comm.send(W, dest=p, tag=11)

    for w in range(W):
        for i in range(2):
            for t in range(T):
                line = all_lines[2*w+i+1]
                tower_infos = line.split(",")
                coordinates = list(map(int, tower_infos[t].split()))
                if(table[coordinates[0]*N+coordinates[1]] == ".0"):  # if there is no tower
                    if(i % 2 == 0):
                        table[coordinates[0]*N+coordinates[1]] = "o6"
                    else:
                        table[coordinates[0]*N+coordinates[1]] = "+8"
        for p in range(1, size):
            # 0: p=1 olacak (row-1)*num_cells to row*num_cells
            row = int((p-1)//int(math.sqrt(size-1)))
            # 1: p=2 olacak (column-1)*num_cells to column*num_cells
            column = int((p-1) % int(math.sqrt(size-1)))
            num_cells = int(N//int(math.sqrt(size-1)))
            data = []
            for i in range(row*num_cells, (row+1)*num_cells):
                data.append(table[i*N+column*num_cells:i *
                            N+column*num_cells+num_cells])
            comm.send(data, dest=p, tag=w)

        rec_data = []
        for p in range(1, size):
            rec_data.append(comm.recv(source=p, tag=w))  # büyük W

        table = []
        b = int(math.sqrt(size-1))  # bir kenar uzunluğu #2
        a = num_cells  # 4
        for i in range(b):
            for k in range(a):
                for j in range(b):
                    for l in range(a):
                        table.append(rec_data[b*i+j][k][l])

    outputFile = open(outputName, "w")
    for i in range(len(table)):
        outputFile.write(table[i][0]+" ")
        if(i % N == N-1):
            outputFile.write("\n")
    outputFile.close()


else:
    N = comm.recv(source=0, tag=10)
    W = comm.recv(source=0, tag=11)
    # num of cells in a side of array
    num_cells = int(N//int(math.sqrt(size-1)))

    for w in range(W):
        p0_data = comm.recv(source=0, tag=w)
        num_of_p = int(math.sqrt(size-1))

        # initializing
        data_rec_u = [".0"]*num_cells
        data_rec_d = [".0"]*num_cells
        data_rec_r = [".0"]*num_cells
        data_rec_l = [".0"]*num_cells
        data_rec_ur = ".0"
        data_rec_ul = ".0"
        data_rec_ll = ".0"
        data_rec_lr = ".0"

        for r in range(8):
            # sağa gönder
            if((rank-1) % num_of_p != num_of_p-1):  # sağda değil
                data_sent_r = [row[-1] for row in p0_data]
                comm.send(data_sent_r, dest=rank+1, tag=w)
            if((rank-1) % num_of_p != 0):
                data_rec_l = comm.recv(source=rank-1, tag=w)

            # sola gönder
            if((rank-1) % num_of_p != 0):  # solda değil
                data_sent_l = [row[0] for row in p0_data]
                comm.send(data_sent_l, dest=rank-1, tag=w)
            if((rank-1) % num_of_p != num_of_p-1):
                data_rec_r = comm.recv(source=rank+1, tag=w)

            # yukarı gönder
            if((rank-1)//num_of_p != 0):  # yukarıda değil
                data_sent_u = p0_data[0]
                comm.send(data_sent_u, dest=rank-num_of_p, tag=w)

            if((rank-1)//num_of_p != num_of_p-1):
                data_rec_d = comm.recv(source=rank+num_of_p, tag=w)

            # aşağı gönder
            if((rank-1)//num_of_p != num_of_p-1):  # aşağıda değil
                data_sent_d = p0_data[-1]
                comm.send(data_sent_d, dest=rank+num_of_p, tag=w)

            if((rank-1)//num_of_p != 0):
                data_rec_u = comm.recv(source=rank-num_of_p, tag=w)

            # sağ üst çapraz
            if((rank-1) % num_of_p != num_of_p-1 and (rank-1)//num_of_p != 0):  # yukarıda ve sağda değil
                data_sent_ur = p0_data[0][num_cells-1]
                comm.send(data_sent_ur, dest=rank-num_of_p+1, tag=w)
            if((rank-1) % num_of_p != 0 and (rank-1)//num_of_p != num_of_p-1):  # solda ve aşağıda değil
                data_rec_ll = comm.recv(source=rank+num_of_p-1, tag=w)

            # sol alt çapraz
            if((rank-1) % num_of_p != 0 and (rank-1)//num_of_p != num_of_p-1):  # solda ve aşağıda değil
                data_sent_ll = p0_data[num_cells-1][0]
                comm.send(data_sent_ll, dest=rank+num_of_p-1, tag=w)
            if((rank-1) % num_of_p != num_of_p-1 and (rank-1)//num_of_p != 0):  # yukarıda ve sağda değil
                data_rec_ur = comm.recv(source=rank-num_of_p+1, tag=w)

            # sol üst çapraz
            if((rank-1) % num_of_p != 0 and (rank-1)//num_of_p != 0):  # solda ve aşağıda değil
                data_sent_ul = p0_data[0][0]
                comm.send(data_sent_ul, dest=rank-num_of_p-1, tag=w)
            # yukarıda ve sağda değil
            if((rank-1) % num_of_p != num_of_p-1 and (rank-1)//num_of_p != num_of_p-1):
                data_rec_lr = comm.recv(source=rank+num_of_p+1, tag=w)

            # sağ alt çapraz
            if((rank-1) % num_of_p != num_of_p-1 and (rank-1)//num_of_p != num_of_p-1):
                data_sent_lr = p0_data[num_cells-1][num_cells-1]
                comm.send(data_sent_lr, dest=rank+num_of_p+1, tag=w)
            if((rank-1) % num_of_p != 0 and (rank-1)//num_of_p != 0):  # solda ve aşağıda değil
                data_rec_ul = comm.recv(source=rank-num_of_p-1, tag=w)

            # making a (num_of_cels+2)**2 array

            all_arr = [0]*(num_cells+2)
            all_arr[0] = [data_rec_ul]+data_rec_u+[data_rec_ur]
            for i in range(num_cells):
                all_arr[i+1] = [data_rec_l[i]]+p0_data[i]+[data_rec_r[i]]
            all_arr[num_cells+1] = [data_rec_ll]+data_rec_d+[data_rec_lr]

            health_points = []
            health_points_inner_arr = []
            for i in range(1, num_cells+1):
                for j in range(1, num_cells+1):
                    health_points_inner_arr.append(int(all_arr[i][j][1]))
                health_points.append(health_points_inner_arr)
                health_points_inner_arr = []

            for i in range(1, num_cells+1):
                for j in range(1, num_cells+1):
                    tower = all_arr[i][j]
                    health = health_points[i-1][j-1]
                    if(tower[0] == "o"):
                        if(all_arr[i-1][j][0] == "+"):  # up
                            health -= 2
                        if(all_arr[i+1][j][0] == "+"):  # down
                            health -= 2
                        if(all_arr[i][j-1][0] == "+"):  # left
                            health -= 2
                        if(all_arr[i][j+1][0] == "+"):  # right
                            health -= 2
                    elif(tower[0] == "+"):
                        if(all_arr[i-1][j][0] == "o"):  # up
                            health -= 1
                        if(all_arr[i+1][j][0] == "o"):  # down
                            health -= 1
                        if(all_arr[i][j-1][0] == "o"):  # left
                            health -= 1
                        if(all_arr[i][j+1][0] == "o"):  # right
                            health -= 1
                        if(all_arr[i-1][j-1][0] == "o"):  # upper-left
                            health -= 1
                        if(all_arr[i-1][j+1][0] == "o"):  # upper-right
                            health -= 1
                        if(all_arr[i+1][j-1][0] == "o"):  # lower-left
                            health -= 1
                        if(all_arr[i+1][j+1][0] == "o"):  # lower-right
                            health -= 1

                    health_points[i-1][j-1] = health

            for i in range(1, num_cells+1):
                for j in range(1, num_cells+1):
                    if(health_points[i-1][j-1] <= 0):
                        all_arr[i][j] = ".0"
                    else:
                        all_arr[i][j] = all_arr[i][j][0] + \
                            str(health_points[i-1][j-1])
            p0_data = []
            for i in range(1, num_cells+1):
                p0_data.append(all_arr[i][1:-1])

        comm.send(p0_data, dest=0, tag=w)
