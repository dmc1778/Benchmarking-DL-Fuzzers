import tensorflow as tf
arg_0=tf.random.uniform(shape=(2, 2, 2), dtype=tf.float16, maxval=None)
arg_1=tf.random.uniform(shape=(2, 2, 2), dtype=tf.int32, maxval=65536)
arg_2=tf.random.uniform(shape=(2, 2, 2), dtype=tf.int32, maxval=65536)
arg_3=''
tf.raw_ops.TensorListScatter(tensor=arg_0, indices=arg_1, 
element_shape=arg_2, name=arg_3)