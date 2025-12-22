Name: [程伟卿 田园]

## Question 1

In the following code-snippet from `Num2Bits`, it looks like `sum_of_bits`
might be a sum of products of signals, making the subsequent constraint not
rank-1. Explain why `sum_of_bits` is actually a _linear combination_ of
signals.

```
        sum_of_bits += (2 ** i) * bits[i];
```

## Answer 1

在 Circom 电路中，`(2 ** i)` 并不是一个变量或信号，而是一个**编译时常量**（编译时已知的确定数值）。因此，表达式 `(2 ** i) * bits[i]` 实际上是：
- `bits[i]`：一个信号变量
- `(2 ** i)`：一个已知的常数系数

在这里对于每个索引 `i`，`(2 ** i)` 是在电路编译时确定的固定值， `bits[i]` 是电路中实际的信号变量，整个表达式 `sum_of_bits` 是形式为：`c₁·s₁ + c₂·s₂ + ... + cₙ·sₙ` 的线性组合，其中 `cᵢ` 是常数，`sᵢ` 是信号。

R1CS（Rank-1 Constraint System）要求约束是线性的，但允许信号与常数的乘法。因为常数在约束系统中不会引入新的变量维度，所以这样的表达式仍然构成秩为1的约束。

---

## Question 2

Explain, in your own words, the meaning of the `<==` operator.

## Answer 2

在 Circom 中，`<==` 运算符是一个**复合运算符**，它同时执行两个操作：

1. **信号赋值**：将右侧表达式的值赋给左侧信号
2. **约束生成**：自动创建一个等式约束，强制左侧信号必须等于右侧表达式

具体来说，`a <== b + c` 等价于：
```circom
a === b + c;  // 创建约束：a 必须等于 b + c
a <-- b + c;   // 赋值：将 b+c 的值赋给 a
```

简而言之，`<==` 用于**中间信号**（非输入/输出信号），它确保电路执行时的实际计算值（赋值）与电路的约束系统（证明验证）保持一致。这是 Circom 中连接"计算"和"证明"的关键机制，保证 prover 不能随意赋值而必须满足约束。

---

## Question 3

Suppose you're reading a `circom` program and you see the following:

```
    signal input a;
    signal input b;
    signal input c;
    (a & 1) * b === c;
```

Explain why this is invalid.

## Answer 3

这个代码片段无效，原因如下：

a、b和c都是电路信号，第四行代码对信号a做了位运算。circom中信号的赋值与约束操作是分开进行的，不能直接在赋值语句中使用位运算。

所以应该对其进行修改：先执行 `a <== (a & 1) * b` 语句来完成位运算并将结果乘上b。接着再使用约束语句 `c===a` 来完成赋值操作。

