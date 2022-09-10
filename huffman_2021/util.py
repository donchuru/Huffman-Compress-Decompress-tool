import bitio
import huffman
import pickle

def read_tree(tree_stream):
    '''Read a description of a Huffman tree from the given compressed
    tree stream, and use the pickle module to construct the tree object.
    Then, return the root node of the tree itself.

    Args:
      tree_stream: The compressed stream to read the tree from.

    Returns:
      A Huffman tree root constructed according to the given description.
    '''

    tree = pickle.load(tree_stream)
    return tree

def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """
    
    if isinstance(tree, huffman.TreeLeaf):
      return tree.getValue()
  
    if bitreader.readbit() == 1:
      return decode_byte(tree.getRight(), bitreader)
    return decode_byte(tree.getLeft(), bitreader)
    #returns decoded byte

def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.
    '''

    tree = read_tree(compressed)

    writingbits = bitio.BitWriter(uncompressed)
    readingbits = bitio.BitReader(compressed)

    flag = True

    while flag == True:
      try:
        decoded_bits = decode_byte(tree, readingbits)
        writingbits.writebits(decoded_bits, 8)
      except:
        flag = False
    writingbits.flush()

def write_tree(tree, tree_stream):
    '''Write the specified Huffman tree to the given tree_stream
    using pickle.

    Args:
      tree: A Huffman tree.
      tree_stream: The binary file to write the tree to.
    '''

    pickle.dump(tree, tree_stream)

def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''

    bitwriter = bitio.BitWriter(compressed)
    bitreader = bitio.BitReader(uncompressed)

    write_tree(tree, compressed)

    encoded_table = huffman.make_encoding_table(tree)

    EOF = False
    while EOF == False:
      try: 
        input_byte = bitreader.readbits(8)
        encoded_byte = encoded_table[input_byte]
        for bit in encoded_byte:
          bitwriter.writebit(bit)

      except EOFError:
        encoded_byte = encoded_table[None]
        EOF = True
        for bit in encoded_byte:
          bitwriter.writebit(bit)
    bitwriter.flush()