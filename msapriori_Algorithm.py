
import sys
import operator


mis_data = {}	# MIS data will be stored in dictionary.
process_data = []	# input data will be stored in a list.

constraint = []	# constraints such as must-have and no-together will be stored in a list. 

# process the input data from input file and store all sequences into process_data list
def read_data(data_file):
	with open(data_file) as f:
		for line in f:
			l = list(line)
			p1 = l.index("{")
			p2 = l.index("}")
			line = line[p1+1:p2]
			l00 = line.split(", ")	# each item in one sequence is stored in a list
			process_data.append(l00) 

# process the parameter data from input file. Store mis data into the mis_data dictionary and constraints into the constraint list.  
def read_mis(mis_file):
	with open(mis_file) as f:
		for line in f:
		    line = line.rstrip()
		    if "=" in line:
			key,value = line.split(" = ")
			if key[0:3] == 'MIS':
				key=key[4:-1]
			mis_data[key]=float(value)
		    if ":" in line:
			a,b = line.split(": ")
			if a == 'cannot_be_together':
				p1 = b.index("{")
                        	p2 = b.index("}")
                        	b = b[p1+1:p2]
				b = b.split(", ")
				
				constraint.append(b[:])
				

			if a == 'must-have':
				b = b[:]
				b = b.split(" or ")
				constraint.append(b[:])
	
						
# check whether one item in the sequence or not. 
def isInseq(item,set):
	if item in set:
		return True
	else:
		return False

# count the support of one item in the data. 
def support_count(item,data):
	n = 0
	for i in data:
		if isInseq(item,i):
			n = n+1
	return n

# count the total number of sequences in the data. 
def size_ofseqs(data):
	return len(data)

# sort all items in a set according to each item's MIS value. 
def sort_items(data,mis):
	dic_seq = {}
	for i in mis.keys():
		for j in data:
			if i in j:
				dic_seq[i]=mis[i]
	sort_items= sorted(dic_seq.items(), key=operator.itemgetter(1))
	return sort_items # sorted items are stored in a list and each item is built as (item, MIS(item)). 

# First scan the data and store all items whose support count is bigger than the MIS value of the first item whose support count >= MIS value in an ordered itemset. 
def first_pass(sort,data):
	 n = size_ofseqs(data)
	 L = []
	 for i in sort:	# i is tuple.
                    if support_count(i[0],data)>= (n* mis_data[i[0]]):
                                L.append(i[0]) # find the first item in sorted items whose support count is not smaller than its mis value. And store it in L as the first one.  
                                p=sort.index(i)
                                sort_after=sort[p+1:len(sort)]
                                for j in sort_after: # insert all item after the first one in order whose support count is bigger than mis value of the first one. 
                                   if support_count(j[0],data)>=(n*mis_data[L[0]]):
                                                        L.append(j[0])
               			return L

#level2-candidate-gen function: It takes an argument L and returns a superset of the set of all frequent 2-itemsets.
def level2_cand_gen(L,sdc):
	n = size_ofseqs(process_data)
	C2=[]
	for l in L:
		if support_count(l,process_data)>=(mis_data[l]*n):
			L0=[]
			p = L.index(l)
			L0=L[p+1:len(L)]
			for h in L0:
				if support_count(h,process_data)>=(mis_data[l]*n) and abs(support_count(h,process_data)-support_count(l,process_data))<=(n*sdc):
					c=[]
					c=[l,h]
					#if isMust_have(must_h,c):
						#if not is_together(c,no_together):
					C2.append(c)
	return C2

# Frequent 1-itemsets F1 are obtained from L. 
def F_1(L,mh):
	F1 = []
	n = size_ofseqs(process_data)
	for l in L:
		if support_count(l,process_data)>=(mis_data[l]*n):
			if l in mh:
				F1.append([l])
	return F1		

# find all subsets from an itemsets. Each subset is shorter than the itemsets by one item. 
def subsets(itemset):
    subset = []
    for i in itemset:
        j = []
        p = itemset.index(i)
        j = itemset[:p]+itemset[p+1:]
        subset.append(j)
    return subset


# MScandidate-gen function: 
def MScandidate_gen(F,sdc):
	C =[]
	n = size_ofseqs(process_data)
    
# join step: generate candidates might be frequent itemsets
	for i in F:
		for j in F:
			if i[0:-1]==j[0:-1] and i[-1]<j[-1] and abs(support_count(i[-1],process_data)-support_count(j[-1],process_data))<=(n*sdc):
				c = []
				c = i[:]
				
				c.append(j[-1])
				#if isMust_have(must_h,c): # check the candidate whether meets the constraints. 
                #        		if not is_together(c,no_together):
				C.append(c)
# prune step: delete some candidates
	for k in C:
        	p = C.index(k)
        	subset = []
        	subset = subsets(k)
		for j in subset:
			if k[0] in j or mis_data[k[0]]==mis_data[k[1]]:
				if j not in F:
					del C[p]
					break	
	
	return C

# Frequent k-itemsets are obtained from C(k). Here k is not smaller than 2. 
def F_k(C_k,mis,data,must_h,no_together):
	F_k = []
	n = size_ofseqs(data)
	for c in C_k:
		if isMust_have(must_h,c): # check the candidate whether meets the constraints. 
			if not is_together(c,no_together):
				
				if support_seq(c,data)>= n*mis_data[c[0]]:
					F_k.append(c)
				
	return F_k	

# scan data and record the support count of an itemset in the data. 
def support_seq(seq,data):
	n = 0
	for i in data:
		for j in seq:
			if j not in i:
				break
		else:
			n = n+1
	return n

# check whether an itemset contains any must-having item. 
def isMust_have(must_h,itemset):
	for i in must_h:
		if i in itemset:
			return True
	return False

# check whether an itemset has any no-together itemset. 	
def is_together(itemset,no_together):
	n = 0
	for i in no_together:
		if i in itemset:
			n = n+1
		if n == 2:
			return True
			
	return False

# Format the output of the project. 
def output(freq_items,data):
	freq_items = freq_items[1:]
	for i in freq_items:
		n = freq_items.index(i)+1
		print 'Frequent %d-itemsets \n' % n
		
		for j in i:
		     j_output = '{' + str(j).strip('[]') + '}'
		     print '\t%d : %s' % (support_seq(j,data), j_output) # the support count of the itemsets. 

		     if len(j)>1:
			j_tail = j[1:]
			
			j_tailcount = support_seq(j_tail,data)	# Tailcount
			#print 'Tailcount = %d' % j_tailcount
		print '\n\tTotal number of freuqent %d-itemsets = %d\n\n' % (n, len(i)) 

def main():
		sort = []
		L = []
		C2 = []
		C_sets = []
		F_sets = []
		
		read_mis(sys.argv[2])
		read_data(sys.argv[1]) # read input file and parameter file from arguments 
		

		must_h = constraint[1]
		no_together = constraint[0]
		#print 'Print constraints: must_have, %s; no_together, %s.' % (must_h, no_together)
		n = size_ofseqs(process_data)
		#print n
		sort = sort_items(process_data,mis_data)
		L= first_pass(sort,process_data)	# Make the first pass over T and produce the seeds L.
		C2 = level2_cand_gen(L,mis_data['SDC'])	# Generate all candidate of 2-itemsets.
		
		
		F_sets.append(L)	# The seeds L is stored in the F_sets at first.
		F_sets.append(F_1(L,must_h)) # the 1-itemsets F_1 is inserted in the F_sets. 
		for i in xrange(2,100,1):	
			if not F_sets[i-1]:		
				del F_sets[-1]
				if len(C_sets)>=1:
					del C_sets[-1]
				break
			else:	# when F_k-1 is not empty
				if i <= 2:	# To generate 2-itemsets candidates. 
					C2 = level2_cand_gen(F_sets[0],mis_data['SDC'])
					C_sets.append(C2)
				else:
					# To generate k-itemets(k>2) candidates. 
					C_sets.append(MScandidate_gen(F_sets[i-1],mis_data['SDC']))
				
				F_sets.append(F_k(C_sets[i-2],mis_data,process_data,must_h,no_together))	#  F_sets is the set of all Frequent itemsets.
	
		output(F_sets,process_data) # Print out all Frequent itemsets. 

	
if __name__ == "__main__": main()
