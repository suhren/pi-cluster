
6.2 MB:

```bash    
wget -c https://norvig.com/big.txt
```

5.3 MB:

```bash
wget -c https://ocw.mit.edu/ans7870/6/6.006/s08/lecturenotes/files/t8.shakespeare.txt
```

On local machine:

```bash
python word_freq_count.py text.txt > counts
python3 word_freq_count.py text.txt > counts
```

On Hadoop:

```bash
python word_freq_count.py text.txt -r hadoop > counts
python3 word_freq_count.py text.txt -r hadoop > counts
```