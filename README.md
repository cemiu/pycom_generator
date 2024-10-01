# PyCoM Generator

Pipeline for creating the PyCoM database; see:
- Website: https://pycom.brunel.ac.uk/
- Paper: https://doi.org/10.1093/bioinformatics/btae166
- Python Library repo: https://github.com/scdantu/pycom


tldr: For UniProtKB proteins:
- Filter to manage size (Swiss-prot only; seq length ≤ 500)
- Extract annocations (`mjolnir db` command)
- Pipeline (`mjolnir process` command):
  - Sequence Alignment with HH-Suite (HH-Blits => HH-Filter)
  - Predict Protein Residue-Residue Contacts / Coevolution matrices with CCMpred

---

This code was written for the creation of the PyCoM database. It was written to run on the [Jade2 HPC](https://www.jade.ac.uk/) at Oxford and the [Young HPC](https://www.rc.ucl.ac.uk/docs/Clusters/Young/) at UCL.

The resulting project/database, PyCoM, can be found on [https://pycom.brunel.ac.uk](https://pycom.brunel.ac.uk).

This git repo is also of interest, as it contains the library for interacting with the database created by this: [https://github.com/cemiu/pycom](https://github.com/cemiu/pycom).

My work on this project was funded by the Department of Computer Science, Brunel University London.

### DATABASE DOWNLOAD

https://pycom.brunel.ac.uk/

### Info

Pipeline tools

Uniclust (for hh-suite)
- http://gwdu111.gwdg.de/~compbiol/uniclust/2022_02/

Sequence alignment
- hhsuite https://github.com/soedinglab/hh-suite

Coevolution matrix
- ccmpred https://github.com/soedinglab/CCMpred
