#include <bits/stdc++.h>
#include <zlib.h>

/**
 * Script for extracting protein sequences from PDB structures
 * 
 * Compile with -lz option for zLib
 * 
 * Input:
 *     line-seperated list of *.ent.gz files in the following format:
 *     xx/pdbIIII.ent.gz
 *     If a different file format / relative path is used, the following line much be adjusted:
 *         cout << file.substr(6, 4) << " " << sequence_from_pdb(pdb_ss) << endl;
 *     such that `file.substr(6, 4)` selects the PDB from the file path.
 *     
 * Output:
 *     line-seperated list of PDB IDs and extracted sequences, seperated by a space
 *         unknown or missing non-terminal residues are denoted by a '.' character
 *     6a01 YVSLADLERAARDVLPGEI[...]     # PDB ID and sequence
 *     5a0z LAWM..............QGPT[...]  # sequence with missing residues
 *     100d -                            # PDB without sequence ('-' character)
 */

using namespace std;

const std::unordered_map<std::string, char> aminoAcidLookup = {
    {"ALA", 'A'}, {"ARG", 'R'}, {"ASN", 'N'}, {"ASP", 'D'},
    {"CYS", 'C'}, {"GLN", 'Q'}, {"GLU", 'E'}, {"GLY", 'G'},
    {"HIS", 'H'}, {"HIP", 'H'}, {"HIE", 'H'}, {"ILE", 'I'},
    {"LEU", 'L'}, {"LYS", 'K'}, {"MET", 'M'}, {"PHE", 'F'},
    {"PRO", 'P'}, {"SER", 'S'}, {"THR", 'T'}, {"TYR", 'Y'},
    {"TRP", 'W'}, {"VAL", 'V'}, // {"SEC", 'U'}, {"PYL", 'O'}, // selenocysteine & pyrrolysine
};

std::stringstream decompressGZFile(const std::string& filename) {
    gzFile gzfile = gzopen(filename.c_str(), "rb");
    if (!gzfile) {
        std::cerr << "Failed to open file " << filename << std::endl;
        return std::stringstream();
    }
    
    char buffer[4096];
    std::stringstream ss;
    int num_read = 0;
    while ((num_read = gzread(gzfile, buffer, sizeof(buffer))) > 0) {
        ss.write(buffer, num_read);
    }

    gzclose(gzfile);
    return ss;
}

string sequence_from_pdb(std::stringstream& pdb) {
    vector<pair<int, char>> v;
    int max_resseq = 0;
    int min_resseq = 10000;
    
    string line;
    while(std::getline(pdb, line)) {
        string statement = line.substr(0, 4); // "ATOM" || "TER "
        if (statement == "TER ") break; // first strand over
        if (statement != "ATOM") continue; // ignore non-atom statements
        
        string atom = line.substr(13, 2);
        if (atom != "CA" && atom != "CB") continue; // only consider C_a or C_b atoms
        string aa = line.substr(17, 3);
        if (atom == "CA" && aa != "GLY") continue; // only consider C_a for glycine
        if (aminoAcidLookup.find(aa) == aminoAcidLookup.end()) continue; // not standard AA

        char aa_s = aminoAcidLookup.at(aa);
        int resseq = stoi(line.substr(23, 4));
        if (resseq > max_resseq)
            max_resseq = resseq;
        if (min_resseq > resseq)
            min_resseq = resseq;

        v.push_back(make_pair(resseq, aa_s));

        float x = stof(line.substr(30, 8));
        float y = stof(line.substr(38, 8));
        float z = stof(line.substr(46, 8));

        // cout << aa_s << " " << resseq << " " << atom << endl;
        // cout << aa_s << " " << resseq << " " << x << " " << y << " " << z << endl;
    }

    if (v.size() > 0) {
        string sequence(max_resseq - min_resseq, '.');
        for (pair<int, char> p : v) {
            sequence[p.first - min_resseq] = p.second;
        }
        return sequence;
    } else return "-";
}

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL);

    vector<string> files;
    string next_file;
    while (getline(cin, next_file)) {
        files.push_back(next_file);
    }

    // cout << files[0] << endl;

    for (auto file : files) {
        auto pdb_ss = decompressGZFile(file);
        cout << file.substr(6, 4) << " " << sequence_from_pdb(pdb_ss) << endl;
        stringstream().swap(pdb_ss);
    }

    return 0;
}
