import numpy as np
import tensorflow as tf
"""
---- returncode=1 ----
stdout> 
stderr> Traceback (most recent call last):
  File "/tmp/tmp1725842672.1796234.py", line 11, in <module>
    x1.set_shape([1, 2])
  File "/home/ubuntu/anaconda3/envs/tf_2.11.0/lib/python3.9/site-packages/tensorflow/python/framework/ops.py", line 1299, in set_shape
    raise ValueError(f"Tensor's shape {self.shape} is not compatible "
ValueError: Tensor's shape (2, 2) is not compatible with supplied shape [1, 2].


"""

x1 = tf.constant([[1, 2], [3, 4]])
x2 = tf.zeros_like(x1)
y = tf.experimental.numpy.remainder(x1, 2)
x1.set_shape([1, 2])
x2.set_shape([1, 2])
y = tf.equal(x2, y)
y = tf.equal(x2, y)
with tf.GradientTape() as tape:
    loss = tf.constant(3)
