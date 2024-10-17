import os, csv, sys
import pandas as pd
import re
sys.path.insert(0, '/home/nimashiri/Benchmarking-DL-Fuzzers/')
from utils.fileUtils import read_txt, postprocess_test_statistics, write_to_csvV2, write_to_csv
from utils.decompose_log import decompose_detections

REG_PTR = re.compile('torch')

executed = False

def decompose_detections_v2(splitted_lines):
    super_temp = []
    j = 0
    indices = []
    while j < len(splitted_lines):
        if REG_PTR.search(splitted_lines[j]):
            indices.append(j)
        if REG_PTR.search(splitted_lines[j]):
            indices.append(j)
        j += 1

    if len(indices) == 1:
        for i, item in enumerate(splitted_lines):
            if i != 0:
                super_temp.append(item)
        super_temp = [super_temp]
    else:
        i = 0
        j = 1
        while True:
            temp = [] 
            for row in range(indices[i], indices[j]):
                temp.append(splitted_lines[row])
            super_temp.append(temp)
            if j == len(indices)-1:
                temp = [] 
                for row in range(indices[j], len(splitted_lines)):
                    temp.append(splitted_lines[row])
                super_temp.append(temp)
                break
            i+= 1
            j+= 1

    return super_temp

class SummarizeTestCases:
    def __init__(self, tool_name, lib_name, iteration, release) -> None:
        self.tool_name = tool_name
        self.lib_name = lib_name
        if tool_name == 'ACETest':
            self.iteration = iteration - 1
        else:
            self.iteration = iteration
        self.release = release
        self.freefuzz_root_path  = f"/media/nimashiri/DATA/testing_results/tosem/{self.tool_name}/{self.lib_name}/{self.iteration}/{self.release}"
        self.deeprel_root_path = f"/media/nimashiri/DATA/testing_results/tosem/{self.tool_name}/{self.lib_name}/{self.iteration}/{self.release}/expr"
        
        if lib_name == 'torch':
            self.nablafuzz_root_path = f"/media/nimashiri/DATA/testing_results/tosem/NablaFuzz/NablaFuzz-PyTorch-Jax/output-ad/{self.iteration}/{self.release}/torch/union/"
        else:
            self.nablafuzz_root_path = f"/media/nimashiri/DATA/testing_results/tosem/NablaFuzz/NablaFuzz-TensorFlow/src/expr_outputs/{self.iteration}/{self.release}/test/logs/"
        
        if lib_name == 'torch':
            full_lib_name = 'pytorch'
            self.docter_root_path = f"/media/nimashiri/DATA/testing_results/tosem/workdir/{full_lib_name}/{self.iteration}/{self.release}+cu118/conform_constr"
        else:
            full_lib_name = 'tensorflow'
            self.docter_root_path = f"/media/nimashiri/DATA/testing_results/tosem/workdir/{full_lib_name}/{self.iteration}/{self.release}/conform_constr"
        
        self.acetest_root_path = f"/media/nimashiri/DATA/testing_results/tosem/{self.tool_name}/Tester/src/output/output_{self.lib_name}_{self.iteration}/{self.release}"
        
        self.titanfuzz_root_path = f"/media/nimashiri/DATA/testing_results/tosem/titanfuzz/Results/{self.lib_name}/{self.release}/{self.iteration}"
        self.atlasfuzz_root_path = f"/media/nimashiri/DATA/testing_results/tosem/code-{self.tool_name}/fewshot/output/{self.lib_name}_demo/{self.iteration}/{self.release}"

        self.execution_flag = True
        
        self.nablafuzz_test_counter  = {
            "SUCCESS": 0,
            "PASS": 0,
            "SKIP": 0,
            "FWD_VALUE": 0,
            "STATUS": 0,
            "FWD_STATUS": 0,
            "REV_STATUS": 0,
            "REV_FWD_GRAD": 0,
            "ND_GRAD": 0,
            "GRAD_VALUE_MISMATCH": 0,
            "REV_STATUS_MISMATCH": 0,
            "VALUE_MISMATCH": 0,
            "DIRECT_CRASH": 0,
            "CRASH": 0, 
            "REV_CRASH": 0,
            "FWD_CRASH": 0,
            "REV_GRAD_FAIL": 0,
            "FWD_GRAD_FAIL": 0,
            "ND_FAIL": 0,
            "ARGS_FAIL": 0,
            "DIRECT_FAIL": 0,
            "GRAD_NOT_COMPUTED": 0,
            "RANDOM": 0,
            "DIRECT_NAN": 0,
            'NAN':0}

        
        self.freefuzz_test_counter = {
            'fail': 0,
            'potential-bug': 0,
            'success': 0,
            'crash': 0,
            'timeout': 0
        }

        self.deeprel_test_counter = {
            'bug': 0,
            'err': 0,
            'fail': 0,
            'neq': 0,
            'success': 0
        }
        
        self.docter_test_counter = {
            'crash': 0,
            'exception': 0,
            'fail': 0,
            'timeout': 0,
        }

        self.ace_test_counter = {
            'invalid': 0,
            'crash': 0,
            'timeout': 0,
            'OOM': 0,
        }

        self.titanfuzz_test_counter = {
            'crash': 0,
            'exception': 0,
            'hangs': 0,
            'flaky': 0,
            'notarget': 0,
            'valid': 0
        }
        
        self.fuzzgpt_test_counter = {
            'exception': 0,
            'crash': 0,
            'syntax': 0,
            'memory': 0,
            'success': 0
        }

        self.exception = re.compile(r"(Integer division by zero|Overflow when unpacking long|out-of-range integer|int too big to convert|ZeroDivisionError|Encountered overflow|float floor division by zero|integer division or modulo by zero)")
        
        self.exception = re.compile(r"Not a directory|ValueError: Could not open|(\[Errno 2\] No such file or directory|File name too long|Is a directory|\; No such file or directory|cannot be opened|does not exist|Error 404: Not Found|Vocabulary file|URL fetch failure on|404 -- Not Found|Could not find directory|Name or service not known|SavedModel file does not exist at|No file or directory found|errors_impl.NotFoundError|FileNotFoundError|NotADirectoryError|FailedPreconditionError|File isn't open for writing|PermissionDeniedError)")

        self.exception = re.compile(r"(Integer division by zero|Overflow when unpacking long|out-of-range integer|int too big to convert|ZeroDivisionError|Encountered overflow|float floor division by zero|integer division or modulo by zero|invalid file|is missing from|required broadcastable shapes|is not available in|unsupported tensor layout:|Please open an issue|Max operator for quantized tensors only works for per tensor quantized tensors|but it does not yet support this behavior|have not yet been created|tensor_array op does not support eager execution|does not exist in the graph|Invalid cross-device link|NotImplementedError|not implemented|NotImplementedErrorNotImplementedError)|Could not set tensor of type long int to a tensor of type float|must be 2-D|Load a module with|parameter must be at least one-dimensional|indices must be an int64 tensor|output_size must be 3|must be Tensor, not|must be Tensor, not type|pickle protocol must be|The algorithm failed to converge because|Exception Message ------------torch\.|Exception Message ------------\(torch.Size\(\[|Exception Message ------------torch.Size\(\[|Unrecognised padding mode|linalg.matrix_norm:|Order  not supported|Expected a floating point|must be Tensor, not numpy.str|is required|cannot compute|Could not infer dtype of NoneType|must be bool, not|must be int, not|Boolean value of Tensor with no values is ambiguous|Cannot specify both|must be non-negative|No rendezvous handler for|must be positive|must be tuple|does not require grad|does not match|out of range|(should be of|must be greater than|Index to scalar can have only|could not create a primitive descriptor|must be divisible by groups|object cannot be interpreted as an integer|Invalid padding string|Expected index|could not create a descriptor|has to be smaller|length must be non-negative|must be float, not str|Low precision dtypes not supported|Order\s\S+\snot supported|Order\s-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\snot supported|not all arguments converted|must be Tensor, not tuple|TypeError: not all arguments|doesn't support|must be Tensor, not str|handles only integral|found negative index|Expected a floating point or complex tensor as input|invalid data type|must transform at least one axis|Unsupported dtype|sizes don't match|value cannot be converted|more operands were provided than specified in the equation|to have non-zero size|must be bool, not float|must be bool, not str|must specify the equation string and at least one operand|invalid index Index|non-existing dimension|all the input arrays must have same number of dimensions|Order inf not supported|did not match|Index tensor must have the same number of dimensions as src tensor|can't convert Sparse layout tensor to numpy|optimizer got an empty parameter list|takes at least 1 positional argument|is not expandable to size|Expected target size|is not a valid value for reduction|must have length|but one of the arguments requires grad|Sum of input lengths does not equal the length of the input dataset|Index should have dimension|selected number k out of range for dimension 0|Index should have dimension|are the same size|Creation of quantized tensor requires quantized|appears multiple times in the list of dims|Index is supposed to be an empty tensor or a vector|must be tuple of ints|std and var only support floating point and complex dtypes|must be Number, not str|must be tuple of ints, but found element of type ellipsis at pos 0|Cannot infer concrete type of torch.nn.Module|optimizer can only optimize Tensors, but one of the params is int|has no|failed to unpack the object|not supported on quantized tensors|cannot be concatenated|TypeError: ellipsis is not a Module subclass|When source and destination are not scalars|must be tuple of Tensors, not Tensor|must be int, not float|but has|apart from dimension 1 and to be smaller size than src|subscript i is repeated for operand 0 but the sizes don't match|the batch number of src and tgt must be equal|Dataset not found or corrupted|Output size is too small|Expected input to be 2D or 3D, got 4D instead|is a built-in class|Sparse CSR tensors do not have strides|Invalid device, must be cuda device|NoneType is not an Optimizer|unsupported format string passed|must be Tensor, not complex|Expected reduction dim 1 to have non-zero size|out of bounds|device type at start of device string|tensors used as indices must be long, int, byte or bool tensors|repeats must be 0-dim or 1-dim tensor|must be Tensor, not bool|grad requires non-empty inputs|Tensor is not an Optimizer|grad requires non-empty inputs|Tensor is not an Optimizer|is not a valid value for quantized engine|must be equal to|rank parameter missing|Device index must not be negative|rank parameter missing|an integer is required|must be bool, not Tensor|Supports 1D or 2D tensors. Got 3D|expected|Index is supposed to be a vector|element is out of|self indexing axis dim should be positive|Index is supposed to be a vector|both arguments to matmul need to be at least|TypeError: cannot assign|must be Tensor, not CrossEntropyLoss|isn't allowed in a leading, non-existing dimension 1|is not supported|must be Tensor, not Conv3d|did not appear in the input|should be the same|exceeds dimension size|TypeError: iteration over a 0-d tensor|only Tensors of floating point dtype can require gradients|only Tensors of floating point dtype can require gradients|Specify the reduction dim with the 'dim' argument|Expected reduction dim 0 to have non-zero size|Please look up dimensions by name|must be int, not bool|Mismatch in dtype|expected indent but found|unsupported operation|could not parse dispatch key: TransformerEncoder|diagonal dimensions cannot be identical|must be greater than or equal to|too many dimensions 'str'|dims cannot be empty|Trying to create tensor with negative dimension|not a sequence|Found dtype Float but expected Long|Found dtype Float but expected Double|must be tuple of Tensors, not dict|must be tuple of Tensors, not int|does not match the shape of the indexed tensor|Invalid number of data points|does not match previous terms|Expected state_dict to be|Padding length too large|inconsistent target size|being empty|required rank|can't convert complex to float|not aligned|should match|must be greater or equal to|must be specified, but not both.|but found element of type Tensor at pos 0|assigned grad has data of a different size|must be name, not int|must be tuple of ints, but found element of type tuple at pos 3|Index tensor must have the same number of dimensions as input tensor|must be Tensor, not ellipsis|must be Tensor, not Linear|Tensors of floating point and complex dtype can require gradients|must be Tensor, not NoneType|which an ellipsis was already found|which does not broadcast with previously seen size|but tensor has no dimensions|no dimension of size|inputs must have the same number of dimensions|are out of bounds for storage|mismatch in length of strides and shape|requiring a storage size of|mismatch in length of strides and shape|can't assign Variable as its own grad|tuple indices must be integers or slices, not tuple|Sparse division requires a scalar or zero-dim dense tensor divisor|This function doesn't handle types other than float and double|Index tensor must have the same number of dimensions as self tensor|Kernel size can't be greater than actual input size|cannot assign 'torch.FloatTensor' as parameter 'weight'|view size is not compatible with input tensor's size and stride|can only be None or contain a single element|chunk expects|Expected timeout argument to be of|'DataLoader' object is not an iterator|KeyError: 0|has no parameter or buffer with name 'weight'|has no parameter or buffer with name|data set to a tensor that requires gradients must be floating point or complex dtype|size mismatch|Expected floating point type for target with class probabilities|for 4D input, output_size must have 2 or 4 elements|you can only change requires_grad flags of leaf variables|Expected dtype int32 or int64 for index|torch.FloatTensor is not a Module subclass|cannot assign 'torch' as child module|cannot register a hook on a tensor that doesn't require gradient|requires a floating point input type|must be Tensor, not list|Expected dtype int64 for index|expects a positive integer|Expected self.dtype to be equal to src.dtype|to match|must be int, not Tensor|invalid index of a|input dtype should be either floating point or complex|step must be greater than zero|expected np.ndarray|must be Number, not Tensor|argument 'sorted' must be bool, not Tensor|argument 'sorted' must be bool, not int|must be Tensor, not torch.dtype|must be Tensor, not numpy.ndarray|is an invalid keyword argument for|expected a matrix|cannot be traced|Could not get name of python class object|Only tensors, lists, tuples of tensors, or dictionary of tensors can be output from traced functions|should be a dict|Expected a value of type|Expected a single top-level function:|must be int, not str|must be tuple of ints, not int|but none of the them have requires_grad|Could not get qualified name for class|only floating-point types are supported as the default type|in_channels must be divisible by groups|must be float, not Tensor|object is not iterable|index out of range in self|Input dimension should be at least|expected sequence of length|elements cannot be converted to Scalar|At least one of 'min' or 'max' must not be None|Tensors must have same number of dimensions:|must be None or torch.Tensor|indices should be either on cpu or on the same device as the indexed tensor|int is not a Module subclass|must be int, not tuple|must be int, not list|Expected reinterpreted_batch_ndims|must be Tensor, not float|but found invalid values|Attempted to create a tensor with names|output subscript a appears more than once in the output|does not contain the correct number of indices for operand|fewer operands were provided than specified in the equation|does not contain the correct number of indices for operand|does not match the number of dimensions|Padding length must be divisible by|upper bound and larger bound inconsistent with step sign|must be torch.dtype|is out of range|inconsistent size|input should have at least 2 dimensions, but has 1 dimensions instead|objects doesn't apply to a 'builtin_function_or_method' object|objects doesn't apply to a 'list' object|only one element tensors can be converted to Python scalars|objects doesn't apply to a 'int' object|A must be batches of square matrices|Expected a floating point or complex tensor as input. Got Long|Expected dim 0 size 4, got 2|only integer tensors of a single element can be converted to an index|expected scalar type Long but found Float|Could not infer dtype of ellipsis|is out of bounds for dimension|legacy constructor expects device type|Expected all tensors to be on the same device|number of dimensions in the tensor input does not match|could not infer output dtype|non-empty 3D or 4D|must be tuple of ints, not NoneType|tensor expected for input|repeats must have the same size as input along dim|Number of dimensions of repeat dims can not be smaller than number of dimensions of tensor|Only Tensors of floating point and complex dtype can require gradients|Mismatch in shape|a leaf Variable that requires grad is being used in an in-place operation|weight should have at least three dimensions|too many indices for tensor of dimension|must match the existing size|Expected value argument|high \<\=|Expected parameter probs|Invalid function argument|needs an argument|must be str|must be Tensor, not builtin_function_or_method|Invalid number of FFT data points|expected to be in range of|objects doesn't apply to a 'float' object|but got|but expected one of|must be tuple of ints, not Tensor|Dimension out of range|must be greater or equal to the number of dimensions in the tensor |shapes cannot be multiplied|received an invalid combination of arguments|\bmust be a\b|must be a matrix|expects a tensor with|must be Tensor, not int)")

        self.exception = re.compile(r"Integer division by zero|Overflow when unpacking long|out-of-range integer|int too big to convert|ZeroDivisionError|Encountered overflow|float floor division by zero|integer division or modulo by zero|do not have a common DType|not understood|The passed vocabulary has at least one repeated term|Unknown activation function|doesnt support setting where|must be scalar, got|has constraint on attr|must be at least a vector|Input matrices must be|rank must be at least|field must specify|must specify|size-incompatible|is not a matrix|Matrix size incompatible|Only one of|has invalid|Could not interpret regularizer identifier|did not contain a loop with signature matching|should be a|must not be None|should be positive, Received|unhashable type|IRFFT requires|Dimension\s-?\d+|cannot convert|Expected func to be callable|returned a result with an error set|must have|and have the same elements as|If there is only one output, it must have the same size as the input|Input matrices must be squares|does not index into param shape|length must be|params must be at least a vector|indices must be at least a vector|dimension length must|but params is empty|Shape must be at least|params must be at least|must be at least minimum|Number of outputs is too big|must be either|must be rank|transpose expects|must be rank|Invalid value in|required broadcastable shapes|Can't concatenate|argument should be either|Expected DataType for argument|must be an iterable|Expected string|Expected list for|should be equal to|must be less than|does not allow negative|Incompatible shapes|could not be broadcast|Tensor conversion requested|Cannot find minimum value of|available for|INVALID_ARGUMENT|Exception encountered when calling|only supports|can only concatenate str|is not defined on an unknown|must both|which is out of scope|Got multiple values for argument|can only be used to|Attempting to capture|Received:|Cannot adap|is not in|params argument given to the optimizer should be an iterable of Tensors or dicts, but got torch\.LongTensor|cannot unpack non-iterable|Expected bool passed to parameter 'dims' of op 'Reverse'|Inputs must be a list or tuple|Unknown keywords argument|takes 0 positional arguments but 1 was given|Value passed to parameter 'input' has DataType int32 not in list of allowed values|Argument `matrix` must have dtype in|'RepeatVector' object is not iterable|must contain objects that are subclass of|not supported between instances of 'range' and 'int'|list indices must be integers or slices, not tuple|Tensor is unhashable\. Instead, use|not supported between instances of|a number is required, not Tensor|Invalid shape|Expected `trainable` argument to be a boolean|is not a callable object|of unsupported type|Cannot iterate over a Tensor with unknown first dimension|Expected an integer value for|Expected bool for argument|Expected int for argument|only length-1 arrays can be converted to Python scalars|x and y must have same first dimension, but have shapes|Expected any non-tensor type, but got a tensor instead\.|object of type 'RaggedTensor' has no len\(\)|PicklingError: Can't pickle|argument must be a tuple of 3 integers|Couldn't find 'checkpoint'|argument for zeros\(\) given by name|Date must be in format|got multiple values for argument|argument must be a list\/tuple or one of|layer should be called on a list of at least|argument of type|Unknown argument|No such layer|Expected binary or unicode string|Invalid argument|Could not convert|The following argument types are supported|incompatible function arguments|unsupported operand type\(s\)|Expected tensor|Keyword argument should be one of|Dimension value must be integer or None or have|EagerTensor of dtype|Keyword argument not understood|Eager execution of tf\.constant with unsupported shape\.|Input must be a SparseTensor|got an unexpected keyword argument|,but got|Cannot convert|operands could not be broadcast together with remapped shapes|Error when checking input|must be a callable|is not compatible with the shape|The last dimension of the inputs to a Dense layer should be defined|doesn't match the broadcast shape|not enough values to unpack|Expected a strictly positive value|Found unvisited input tensors that are disconnected from the outputs|tuple index out of range|must be set|argument must be a tuple of 1 integers|is larger than the maximum possible size|The input must have 3 channels|invalid literal for|Could not start gRPC server|Failed to convert a NumPy array to a Tensor|must be one of|weights can not be broadcast to values|Unkown value for|Tensor conversion requested dtype float32 for Tensor with dtype float64|einstein sum subscripts string contains too many subscripts for|object too deep for desired array|Unsupported value for argument axis|was expecting|Causal padding is only supported for|Tensor conversion requested dtype float64 for Tensor with dtype float32|Slicing dataset elements is not supported for rank 0|all input arrays must have the same shape|Could not interpret metric identifier|Tensor conversion requested dtype int64 for Tensor with dtype int32|but the layer was expecting 1 weights|must be a tuple of three integers|When setting|No such job in cluster|Must specify an explicit|Empty or None dump root|Tensor conversion requested dtype int32 for Tensor with dtype float32|Unbatching a tensor is only supported for rank|list index out of range|could not broadcast input array from shape|are not compatible|Output tensors of a Functional model must be the output of a|is encountered while parsing the device spec|Input operand 1 has a mismatch in its core dimension 0|The truth value of an array with more than one element is ambiguous|NoneFile|Unrecognized device|must have rank 0|cannot reshape array of size 5 into shape|Too many elements provided|not compatible with supplied shape|are incompatible|Either provide more data, or a different value for the|Elements in elems must be|cannot reshape array of size|decay is deprecated in the new Keras optimizer|Dimensions 2 and 3 are not compatible|got invalid value|too many indices for array|Seed must be between|must have at least 2 dimensions|Can't convert Python sequence with mixed types to Tensor|must have rank 1|Data cardinality is ambiguous|Vocabulary file abc does not exist|All layers in a Sequential model should have a single output tensor|Cast string to int32 is not supported|with an unsupported type|Dimensions 21 and 6 are not compatible|cannot obtain value for tensor|cannot reshape array of size 4 into shape|except for the last dimension|must be 1, 2, or 3|must be 3, 4 or 5|Could not interpret loss function identifier|The requested array has an inhomogeneous shape after 1 dimensions|don't have the same nested structure|is not supported with explicit padding|Tensor conversion requested dtype float32 for Tensor with dtype int32:|Found input tensor cannot be reached given provided output tensors|Found unexpected instance while processing input|not in range|must have either 3 or 4 dimensions|Input has undefined rank|do not form a valid|was expected to be a|is not in the list of allowed values|Only one input size may be|Input rank should be|Index out of range|but the requested shape|LinAlgError|Matrix is not positive definite|must have the same dtype|can't be cast to the desired output type|must match the size of tensor|grad can be implicitly created only for scalar outputs|is invalid for input|too many values to unpack|InvalidArgumentError|object does not support|doesn't exist for this backend|are supported for now|Unrecognised padding mode linear|padding with non-constant padding are supported for now|Could not find device for node|incompatible with the layer|argument must be a tuple of 2 integers|Inputs to a layer should be tensors|but it received|Please pass these args as kwargs instead")

        self.crash = re.compile(r"(INTERNAL ASSERTION FAILED|JIT compilation failed|Aborted|Non-OK-status|RecursionError|InternalError:|Check failed|floating point exception|Segmentation fault|dumped|bus error|double free)")
             
        self.out_of_memory_pattern = re.compile(r"(Failed to create cuFFT batched plan with scratch allocator|CUDA_ERROR_OUT_OF_MEMORY|OOM|can't allocate memory|Unable to allocate|OOM when allocating|out of memory|Killed)")

        self.exception = re.compile(r"(cudnnFinalize Failed|Unsupported ONNX opset version|Inconsistent configuration parameters|Don't know how to quantize with default settings for torch.bfloat16|appears to not have been used in the graph|CUDA error: device-side assert triggered|cuDNN version incompatibility|PyTorch is not linked with support for vulkan devices|CUDA error: invalid device|Boolean value of Tensor with more than one value is ambiguous|expected, but not set|Invalid configuration parameters|from NoneKeyError|NoneKeyError|The Session graph is empty|is not compatible with eager execution|when eager execution is enabled|No module named|cannot import|ModuleNotFoundError|ImportError|NameError|UnboundLocalError)")
        
        self.exception = re.compile(r"assert.*==.*\(.+,\s*.+\)|AssertionError")
        
        self.exception = re.compile(r"(AssertionError)")
    
        self.syntax_pattern = re.compile(r"(SyntaxError|IndentationError|expected an indented block)")
        
        self.exception = re.compile(r"(object has no attribute|AttributeError|has no attribute)")

        self.exception = re.compile(r"(object has no attribute|AttributeError|has no attribute|Failed to mutate parameter|object is not|Failed to create cuFFT batched plan with scratch allocator|has too many elements|sizes input must be|Sliding window ksize for dimension 1 was zero|Computed output size would be negative|filter must not have zero elements|No algorithm worked|input depth must be evenly divisible by filter depth|should be larger than|\b,\sgot\b|got shape|Invalid reduction arguments|Invalid reduction dimension|doesnt support setting out|must be specified except when you are not providing|Can't pin tensor constructed from a variable|Don't set the|Missing required argument|Missing argument|`classes` should be|is not defined|Name 'nan' not found in|referenced before assignment|is not needed when a module doesn't have any parameter|Did you initialize the RPC framework|takes no keyword arguments|is not yet supported with named tensors|algorithm is not applicable when the number of A rows|Output 0 of ViewBackward0 is a view and is being modified inplace|is not registered|Trying to backward through the graph a second time|RPC has not been initialized|trying to initialize the default process group twice|Unexpected keyword arguments:|Please use torch.jit.script or torch.jit.trace to script your|This function was deprecated since version|PyTorch is not linked with support for mps devices|Default process group has not been initialized, please make sure to call init_process_group|Unknown keywords argument\(s\)|got multiple values for keyword argument 'filters'|You may be trying to pass Keras symbolic|You can work around this limitation by putting the operation in a custom Keras layer|This error will also get raised if you try asserting a symbolic|TypeError: 'TakeDataset' object is not an iterator|TypeError: Invalid `datasets`|Expected a TensorFlow function for which to generate a signature|used 2 times in the model. All layer names should be unique.|must be called at program startup|Can't instantiate abstract class LinearOperator with abstract methods|object is not callable|only integer scalar arrays can be converted to a scalar index|required positional argument|To specify the output signature you need to provide either the|object is not subscriptable|Scalar tensor has no|were given|takes no arguments|Eager execution of tf.constant with unsupported shape|Cannot iterate over a scalar tensor|file already exists|if you need to get a new output Tensor|You must compile your model before|Can't convert non-rectangular Python sequence to Tensor|Please ensure you are using a|This model has not yet been built|Physical devices cannot be modified after being initialized|element 0 of tensors does not require grad|a view of a leaf Variable that requires grad is being used in an in-place operation)")

        
    def count_freefuzz_test_cases(self):
        global executed
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')
            
        directory_path = os.listdir(self.freefuzz_root_path)
        directories = [item for item in directory_path if os.path.isdir(os.path.join(self.freefuzz_root_path, item))]
        for dir_ in directories:
            current_dir = os.path.join(self.freefuzz_root_path, dir_)
            for oracle in ['fail', 'potential-bug', 'success']:
                current_oracle = os.path.join(current_dir, oracle)
                current_apis = os.listdir(current_oracle)
                for api in current_apis:
                    if api in target_data:
                        test_files_path = os.path.join(current_oracle, api)
                        test_files_list = os.listdir(test_files_path)
                        py_file_count = len([file for file in test_files_list if file.endswith('.py')])
                        self.freefuzz_test_counter[oracle] += py_file_count
                        
        crashed_tests = read_txt(os.path.join(self.freefuzz_root_path,'runcrash.txt'))
        timedout_tests = read_txt(os.path.join(self.freefuzz_root_path,'timeout.txt'))
        
        self.freefuzz_test_counter['crash'] = len(crashed_tests)
        self.freefuzz_test_counter['timeout'] = len(timedout_tests)
        
        output_data = [self.lib_name, self.iteration, self.release] + list(self.freefuzz_test_counter.values())
        
        if not executed:
            headers = list(self.freefuzz_test_counter.keys())
            headers.insert(0, 'Library')
            headers.insert(1, 'Iteration')
            headers.insert(2, 'Release')

            write_to_csvV2(headers, "numtests" , self.tool_name)
            executed = True
        write_to_csvV2(output_data, "numtests" , self.tool_name)
        self.freefuzz_test_counter = {key: 0 for key in self.freefuzz_test_counter}
        
    def count_deeprel_test_cases(self):
        global executed
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')

        directories = ['output-0']
        for dir_ in directories:
            current_dir = os.path.join(self.deeprel_root_path, dir_)
            all_dirs = os.listdir(current_dir)
            for pair in all_dirs:
                
                if "+" not in pair:
                    continue
                apis_extracted = pair.split('+')
                api_name =apis_extracted[0]
                if api_name not in target_data:
                    continue
                current_api_pair= os.path.join(current_dir, pair)
                for oracle in ['err', 'fail', 'neq', 'success']:
                    target_ = os.path.join(current_api_pair, oracle)
                    if not os.path.exists(target_):
                        continue
                    test_files_list = os.listdir(target_)
                    py_file_count = len([file for file in test_files_list if file.endswith('.py')])
                    self.deeprel_test_counter[oracle] += py_file_count
        output_data = [self.lib_name, self.iteration, self.release] + list(self.deeprel_test_counter.values())
        
        if not executed:
            headers = list(self.deeprel_test_counter.keys())
            headers.insert(0, 'Library')
            headers.insert(1, 'Iteration')
            headers.insert(2, 'Release')

            write_to_csvV2(headers, "numtests", self.tool_name)
            executed = True
        write_to_csvV2(output_data, "numtests", self.tool_name)
        self.deeprel_test_counter = {key: 0 for key in self.deeprel_test_counter}

    def count_nablafuzz_test_cases(self):
        global executed
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')

        if self.lib_name == 'torch':
            current_data = read_txt(os.path.join(self.nablafuzz_root_path, 'log.txt'))
            decomposed_data = decompose_detections_v2(current_data)
            for line in decomposed_data:
                if not line:
                    continue
                if line[0] in target_data:
                    for subline in line:
                        if 'torch.' in subline:
                            continue
                        dict_data = eval(subline)
                        for key, value in dict_data.items():
                            if key in self.nablafuzz_test_counter.keys():
                                self.nablafuzz_test_counter[key] += value
                            else:
                                self.nablafuzz_test_counter[key] = 0
            out_data = [self.lib_name, self.iteration, self.release]  + list(self.nablafuzz_test_counter.values())

            if not executed:
                headers = list(self.nablafuzz_test_counter.keys())
                headers.insert(0, 'Library')
                headers.insert(1, 'Iteration')
                headers.insert(2, 'Release')
                write_to_csvV2(headers, "numtests", self.tool_name)
                executed = True
            
            write_to_csvV2(out_data, "numtests" , self.tool_name)

        else:
            dirs = os.listdir(os.path.join(self.nablafuzz_root_path))
            for dir in dirs:
                current_dir = os.path.join(self.nablafuzz_root_path, dir)
                if os.path.isdir(current_dir):
                    current_data = read_txt(os.path.join(current_dir, 'test-log.txt'))
                    for line in current_data:
                        api, dict_str = line.split(' ', 1)
                        if api in target_data:
                            dict_data = eval(dict_str)
                            for key, value in dict_data.items():
                                if key in self.nablafuzz_test_counter:
                                    self.nablafuzz_test_counter[key] += value
                                else:
                                    self.nablafuzz_test_counter[key] = 0
            out_data = [self.lib_name, self.iteration, self.release]  + list(self.nablafuzz_test_counter.values())

            if not executed:
                headers = list(self.nablafuzz_test_counter.keys())
                headers.insert(0, 'Library')
                headers.insert(1, 'Iteration')
                headers.insert(2, 'Release')
                write_to_csvV2(headers, "numtests", self.tool_name)
                executed = True
            
            write_to_csvV2(out_data, "numtests" , self.tool_name)
    
    def count_docter_test_cases(self):
        global executed
        def count_docTer_crash(crash_records):
            count = 0
            for j in range(1, len(crash_records)):
                split_records = crash_records[j].split(',')
                count += int(split_records[2])
            return count
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')
            
        directory_path = os.listdir(self.docter_root_path)
        crash_records = read_txt(os.path.join(self.docter_root_path, 'bug_list'))
        
        directories = [item for item in directory_path if os.path.isdir(os.path.join(self.docter_root_path, item))]
        for dir_ in directories:
            dir__ = ".".join(dir_.split('.')[0:-1])
            if dir__ in target_data:
                current_dir = os.path.join(self.docter_root_path, dir_)
                if os.path.isdir(current_dir):
                    if os.path.isfile(os.path.join(current_dir, 'failure_record')):
                        fail_records = read_txt(os.path.join(current_dir, 'failure_record'))
                        self.docter_test_counter['fail'] += len(fail_records)
                    if os.path.isfile(os.path.join(current_dir, 'exception_record')):
                        exception_records = read_txt(os.path.join(current_dir, 'exception_record'))
                        self.docter_test_counter['exception'] += len(exception_records)
                    if os.path.isfile(os.path.join(current_dir, 'timeout_record')):
                        timeout_record = read_txt(os.path.join(current_dir, 'timeout_record'))
                        self.docter_test_counter['timeout'] += len(timeout_record)
                
        self.docter_test_counter['crash'] += count_docTer_crash(crash_records)
 
        output_data = [self.lib_name, self.iteration, self.release] + list(self.docter_test_counter.values())

        if not executed:
            headers = list(self.docter_test_counter.keys())
            headers.insert(0, 'Library')
            headers.insert(1, 'Iteration')
            headers.insert(2, 'Release')

            write_to_csvV2(headers, "numtests", self.tool_name)
            executed = True
        write_to_csvV2(output_data, "numtests" , self.tool_name)
        self.docter_test_counter = {key: 0 for key in self.docter_test_counter}
        
    def count_ace_test_cases(self):
        global executed
        if self.lib_name== 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')

        results = pd.read_csv(os.path.join(self.acetest_root_path, 'res.csv'), encoding='utf-8', sep=',')
        filtered_results = results[results['api'].isin(target_data)]
        
        self.ace_test_counter['invalid'] = filtered_results.iloc[:, 5].sum()
        self.ace_test_counter['crash'] = filtered_results.iloc[:, 6].sum()
        self.ace_test_counter['timeout'] = filtered_results.iloc[:, 7].sum()
        self.ace_test_counter['OOM'] = filtered_results.iloc[:, 8].sum()

        output_data = [self.lib_name, self.iteration, self.release] + list(self.ace_test_counter.values())
        
        if not executed:
            headers = list(self.ace_test_counter.keys())
            headers.insert(0, 'Library')
            headers.insert(1, 'Iteration')
            headers.insert(2, 'Release')

            write_to_csvV2(headers, "numtests", self.tool_name)
            executed = True
        write_to_csvV2(output_data, "numtests" , self.tool_name)
        self.ace_test_counter = {key: 0 for key in self.ace_test_counter}
    
    def count_titanfuzz_test_cases(self):
        global executed
        if self.lib_name== 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')

        target_dirs = ['crash', 'exception', 'hangs', 'flaky', 'notarget', 'valid']
        try:
            for dir_ in target_dirs:
                current_target_dir = os.path.join(self.titanfuzz_root_path, dir_)
                py_files = os.listdir(current_target_dir)
                if py_files:
                    for j, file_ in enumerate(py_files):
                        api_name = file_.split('_')[0]
                        if api_name in target_data:
                            self.titanfuzz_test_counter[dir_] += 1
                else:
                    self.titanfuzz_test_counter[dir_] += len(py_files)
                        
            output_data = [self.lib_name, self.iteration, self.release] + list(self.titanfuzz_test_counter.values())

            if not executed:
                headers = list(self.titanfuzz_test_counter.keys())
                headers.insert(0, 'Library')
                headers.insert(1, 'Iteration')
                headers.insert(2, 'Release')
                write_to_csvV2(headers, "numtests", self.tool_name)
                executed = True
            
            write_to_csvV2(output_data, "numtests" , self.tool_name)
            self.titanfuzz_test_counter = {key: 0 for key in self.titanfuzz_test_counter}
        
        except Exception as e:
            print(e)
    
    def count_atlasfuzz_test_cases(self):
        global executed    
        if self.lib_name == 'torch':
            target_data = read_txt('data/torch_apis.txt')
        else:
            target_data = read_txt('data/tf_apis.txt')

        _path_to_logs_old = f"/media/nimashiri/DATA/testing_results/tosem/code-{self.tool_name}/fewshot/output/{self.lib_name}_demo/{self.iteration}/{self.release}/{self.release}.txt"
        log_data_latest = read_txt(_path_to_logs_old)
        log_decomposed = decompose_detections(log_data_latest)
        try:
            for j, log in enumerate(log_decomposed):
                if "Processing file" in log[0]:
                    api_name = log[0].split('/')[-2]
                    if api_name == 'PyTorch' or api_name == 'TensorFlow':
                        continue
                    if api_name in target_data:
                        exception_flag = False
                        success_flag = False
                        crash_flag = False
                        memory_flag = False
                        syntax_flag = False
                        
                        
                        log_combined = "\n".join(log)
                        exception_flag_ = self.exception.search(log_combined)
                        crash_flag_ = self.crash.search(log_combined)
                        memory_flag_ = self.out_of_memory_pattern.search(log_combined)
                        syntax_flag_ = self.syntax_pattern.search(log_combined)
                        if exception_flag_:
                            exception_flag = True
                            self.fuzzgpt_test_counter['exception'] += 1
                        elif crash_flag_:
                            crash_flag = True
                            self.fuzzgpt_test_counter['crash'] += 1
                        elif memory_flag_:
                            memory_flag = True
                            self.fuzzgpt_test_counter['memory'] += 1
                        elif syntax_flag_:
                            syntax_flag = True
                            self.fuzzgpt_test_counter['syntax'] += 1
                        else:
                            success_flag = True
                            self.fuzzgpt_test_counter['success'] += 1
                        
                        if not any([exception_flag, crash_flag, memory_flag, syntax_flag, success_flag]):
                            print('I came here')
                            
                            
            output_data = [self.lib_name, self.iteration, self.release] + list(self.fuzzgpt_test_counter.values())
            if not executed:
                headers = list(self.fuzzgpt_test_counter.keys())
                headers.insert(0, 'Library')
                headers.insert(1, 'Iteration')
                headers.insert(2, 'Release')
                write_to_csvV2(headers, "numtests", self.tool_name)
                executed = True
                    
            write_to_csvV2(output_data, "numtests" , self.tool_name)
            self.fuzzgpt_test_counter = {key: 0 for key in self.fuzzgpt_test_counter}
        except Exception as e:
            print(e)

if __name__ == '__main__':
    
    lib = {
        'torch': ['2.0.0', '2.0.1', '2.1.0'],
        'tf': ['2.11.0', '2.12.0', '2.13.0', '2.14.0'],
    }
    tool_name = 'NablaFuzz'
    tool_name_low = 'nablafuzz'
    
    if not os.path.isfile(f"statistics/numtests/{tool_name}_1.csv"):
        for k, v in lib.items():  
            for iteration in [1, 2, 3, 4, 5]:
                for release in v:
                    print(f'Library: {k}, Iteration: {iteration}, Release: {release}')
                    obj_= SummarizeTestCases(tool_name, k, iteration, release)
                    function_call = f'obj_.count_{tool_name_low}_test_cases()'
                    eval(function_call)
                    
    lib = {
        'torch': ['2.0.0', '2.0.1', '2.1.0'],
        'tf': ['2.11.0', '2.12.0', '2.13.0', '2.14.0'],
    }
    
    value_holder = []
    for k, v in lib.items():
        for release in v:
            data = pd.read_csv(f"statistics/numtests/{tool_name}_1.csv")
            value_holder.append(postprocess_test_statistics(data, tool_name, k, release))
    headers = list(data.columns.values)
    df = pd.DataFrame(value_holder, columns=headers)
    df.to_csv(f"statistics/numtests/{tool_name}_2.csv", index=False)