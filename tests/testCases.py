from scripting.parser import Node

def syntaxTree():
	'Iterator returning syntax trees representing an expression, the value of each expression, and a name for the test'

	# 1 + 1
	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
			Node('literal',[],1),
		],
		'add'
	)
	ans = 2
	yield tree,ans,'simple_add'

	# (3 * 4) / 2
	tree = Node(
		'functioncall',
		[
			Node(
				'functioncall',
				[
					Node('literal',[],3),
					Node('literal',[],4),
				],
				'multiply'
			),
			Node('literal',[],2),
		],
		'divide'
	)
	ans = 6

	yield tree,ans,'nested_expression'

	# 'bananas'
	tree = Node('literal',[],'bananas')
	ans = 'bananas'

	yield tree,ans,'string_literal'

	# 3 % 2
	tree = Node(
		'functioncall',
		[
			Node('literal',[],3),
			Node('literal',[],2),
		],
		'mod'
	)
	ans = 1

	yield tree,ans,'modulus'

	# 7/2
	tree = Node(
		'functioncall',
		[
			Node('literal',[],7),
			Node('literal',[],2),
		],
		'divide'
	)
	ans = 3

	yield tree,ans,'integer_division'

	# 3-2
	tree = Node(
		'functioncall',
		[
			Node('literal',[],3),
			Node('literal',[],2),
		],
		'subtract'
	)
	ans = 1

	yield tree,ans,'subtraction'

	# if 1: 2
	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
			Node('literal',[],2),
		],
		'if'
	)
	ans = 2

	yield tree,ans,'simple_if'

	# if 0: 2; else: 3
	tree = Node(
		'functioncall',
		[
			Node('literal',[],0),
			Node('literal',[],2),
			Node('literal',[],3),
		],
		'if'
	)
	ans = 3

	yield tree,ans,'simple_if_else'

	# foo = 1; if 0: foo = 2; else: 3; foo
	tree = Node(
		'statement_list',
		[
			Node('assignment',[Node('literal',[],1)],'foo'),
			Node(
				'functioncall',
				[
					Node('literal',[],0),
					Node('assignment',[Node('literal',[],2)],'foo'),
					Node('literal',[],3),
				],
				'if'
			),
			Node('variable',[],'foo'),
		]
	)
	ans = 1

	yield tree,ans,'if_test_before_eval'

	# foo = 1; if 1: foo=2; else: 3; foo
	tree = Node(
		'statement_list',
		[
			Node('assignment',[Node('literal',[],1)],'foo'),
			Node(
				'functioncall',
				[
					Node('literal',[],1),
					Node('assignment',[Node('literal',[],2)],'foo'),
					Node('literal',[],3),
				],
				'if'
			),
			Node('variable',[],'foo'),
		]
	)
	ans = 2

	yield tree,ans,'if_test_before_eval'

	# min([3,4,2])
	tree = Node(
		'functioncall',
		[
			Node('literal',[],4),
			Node('literal',[],2),
			Node('literal',[],3),
		],
		'min'
	)
	ans = 2

	yield tree,ans,'min'

	# max([3,4,2])
	tree = Node(
		'functioncall',
		[
			Node('literal',[],4),
			Node('literal',[],2),
			Node('literal',[],3),
		],
		'max'
	)
	ans = 4

	yield tree,ans,'max'

	# max([3,4,2])
	tree = Node(
		'functioncall',
		[
			Node('literal',[],[3,4,2]),
		],
		'max'
	)
	ans = 4

	yield tree,ans,'max list'

	# sum = 0; for i in [3,4,2]: sum += i; sum
	tree = Node(
		'statement_list',
		[
			Node(
				'assignment',
				[Node('literal', [], 0)],
				'result'
			),
			Node(
				'functioncall',
				[
					Node('literal',[],[1,2,3]),
					Node(
						'block',
						[
							Node(
								'assignment',
								[
									Node(
										'functioncall',
										[
											Node('functioncall', [], 'next'),
											Node('variable', [], 'result'),
										],
										'add'
									)
								],
								'result'
							)
						]
					)
				],
				'each'
			),
			Node('variable',[],'result'),
		]
	)
	ans = 6

	yield tree,ans,'iteration_and_assignment'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
			Node('literal',[],3),
			Node('literal',[],[0]),
		],
		'all'
	)
	ans = 0

	yield tree,ans,'all_with_list_of_zero'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
			Node('literal',[],3),
			Node('literal',[],6),
		],
		'all'
	)
	ans = 1

	yield tree,ans,'all_nonzero_integers'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
			Node('literal',[],0),
			Node('literal',[],1),
		],
		'all'
	)
	ans = 0

	yield tree,ans,'all_with_zero'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],0),
			Node('literal',[],0),
			Node('literal',[],0),
		],
		'all'
	)
	ans = 0

	yield tree,ans,'all_zeros'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],0),
			Node('literal',[],0),
			Node('literal',[],0),
		],
		'any'
	)
	ans = 0

	yield tree,ans,'any_zeros'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],0),
			Node('literal',[],1),
			Node('literal',[],0),
		],
		'any'
	)
	ans = 1

	yield tree,ans,'any_ones_zeroes'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],0),
		],
		'not'
	)
	ans = 1

	yield tree,ans,'not_zero'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
		],
		'not'
	)
	ans = 0

	yield tree,ans,'not_1'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],[1]),
		],
		'not'
	)
	ans = 0

	yield tree,ans,'not_list_1'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],[1]),
			Node('literal',[],[5]),
		],
		'range'
	)
	ans = [1,2,3,4]

	yield tree,ans,'range'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],[-1]),
			Node('literal',[],[-5]),
			Node('literal',[],[-1]),
		],
		'range'
	)
	ans = [-1,-2,-3,-4]

	yield tree,ans,'range_backwards'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],[-1]),
			Node('literal',[],[-5]),
			Node('literal',[],[-1]),
		],
		'less'
	)
	ans = False

	yield tree,ans,'less_fail'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],-1),
			Node('literal',[],-5),
			Node('literal',[],-8),
		],
		'less'
	)
	ans = True

	yield tree,ans,'less'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
			Node('literal',[],0),
		],
		'more'
	)
	ans = False

	yield tree,ans,'more_fail'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
		],
		'more'
	)
	ans = True

	yield tree,ans,'more_no_args'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
			Node('literal',[],1.2),
			Node('literal',[],3),
			Node('literal',[],4),
		],
		'more'
	)
	ans = True

	yield tree,ans,'more'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
			Node('literal',[],1.0),
			Node('literal',[],1),
			Node('literal',[],1),
		],
		'equal'
	)
	ans = True

	yield tree,ans,'equal'

	tree = Node(
		'functioncall',
		[
			Node('literal',[],1),
			Node('literal',[],1.1),
			Node('literal',[],1),
			Node('literal',[],1),
		],
		'equal'
	)
	ans = False

	yield tree,ans,'equal_fail'
