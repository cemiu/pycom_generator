# PyCoM Generator

This code was written for the creation of the PyCoM database. It was written to run on the [Jade2 HPC](https://www.jade.ac.uk/) at Oxford and the [Young HPC](https://www.rc.ucl.ac.uk/docs/Clusters/Young/) at UCL.

The resulting project/database, PyCoM, can be found on [https://pycom.brunel.ac.uk](https://pycom.brunel.ac.uk).

This git repo is also of interest, as it contains the library for interacting with the database created by this: [https://github.com/cemiu/pycom](https://github.com/cemiu/pycom).

My work on this project was funded by the Department of Computer Science, Brunel University London.

### DATABASE DOWNLOAD

https://pycom.brunel.ac.uk/

### Info

Pipeline tools

Link to uniprot databases
	- http://gwdu111.gwdg.de/~compbiol/uniclust/2022_02/

Sequence alignment
- hhsuite https://github.com/soedinglab/hh-suite

Coevolution matrix
- ccmpred https://github.com/soedinglab/CCMpred

### DATABASE CONTENT

	- Uniprot ID
	- protein name / sequence / number of residues
	- organism name / taxonomy
	- list of PDBs
	- Enzyme classification ID
	- CATH classification ID
	- secondary srtucture composition
		- %Helix
		- %Beta
		- %Coil/turn
 	- keywords (PTMs, others; see. https://www.uniprot.org/help/keywords)
	- diseases
	- cofactors
	- ligand/substrate
