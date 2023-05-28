#!/bin/bash
function hello
{
	set -x;
	awk -f hello.txt 'hello.txt';
}
hello

