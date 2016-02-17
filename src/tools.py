"""                                                                              
 Text-Machine Lab: MUTT  

 File Name : tools.py
                                                                              
 Creation Date : 17-02-2016
                                                                              
 Created By : Renan Campos                                               
                                                                              
 Purpose : Algorithms shared by multiple modules.

"""

def edit_distance(s1, s2):
  """
    Quantifies how dissimilar two strings are to one another 
    by counting the minimum number of operations required 
    to transform one string into the other. 
    (Wikipedia explaination)
  """

  m=len(s1)+1
  n=len(s2)+1

  tbl = {}
  for i in range(m): tbl[i,0]=i
  for j in range(n): tbl[0,j]=j
  for i in range(1, m):
    for j in range(1, n):
      cost = 0 if s1[i-1] == s2[j-1] else 1
      tbl[i,j] = min(tbl[i, j-1]+1, tbl[i-1, j]+1, tbl[i-1, j-1]+cost)

  return tbl[i,j]

