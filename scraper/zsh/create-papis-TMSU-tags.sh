#!/bin/zsh

# Script to add TMSU tags to Papis documents based on contents of info.yaml files
# Options:
#		--all : Applies tags to all Papis documents; also suppresses script output
#			-a (alias)

if [[ "$1" = "--all" || "$1" = "-a" ]]; then
	for subdir in $PAPIS_LIBRARY/*/; do
		info="$subdir/info.yaml"
		if [[ -f "$info" ]]; then
			tags=$("$HOME/Source/get-papis-tags.py" "$info")
			papers=("$subdir"/*.pdf(N))
			(($#papers == 0)) || tmsu tag --tags="$tags" $papers
		fi
	done
else
	papis_dir=$1

	if [[ ! -d "$papis_dir" ]]; then
		echo "Directory does not exist!"
		exit 1
	fi

	info="$papis_dir/info.yaml"

	if [[ -f "$info" ]]; then
		tags=$("$HOME/Source/get-papis-tags.py" "$info")
		papers=("$papis_dir"/*.pdf(N))
		(($#papers == 0)) || tmsu tag --tags="$tags" $papers
		echo "Papers successfully tagged:"
		for paper in $papers; do
			echo "\t$paper"
		done
		echo "Tags applied:"
		for tag in "${=tags}"; do
			echo "\t$tag"
		done
	else
		echo "Info file 'info.yaml' not found in directory '$papis_dir'!"
		exit 1
	fi
fi
