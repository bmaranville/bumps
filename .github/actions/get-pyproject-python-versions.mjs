import { readFileSync } from "fs";
import assert from "assert";

function parsePyproject() {
  try {
    const pyprojectToml = readFileSync('pyproject.toml', 'utf8');
    const requiresMatch = pyprojectToml.match(/requires-python\s*=\s*['"]([^'"]+)['"]/);
    if (!requiresMatch) {
      throw new Error("no reuires-python key-value found");
    }
    const requiresPython = requiresMatch[1];
    const minVerMatch = requiresPython.match(/>=(\d+)\.(\d+)/);
    if (!minVerMatch) {
      throw new Error("No minimum 'python-requires' version specified in pyproject.toml with '>='")
    }
    const maxVerMatch = requiresPython.match(/<=(\d+)\.(\d+)/);
    if (!maxVerMatch) {
      throw new Error("No maximum 'python-requires' version specified in pyproject.toml with '<='");
    }
    if (minVerMatch[1] !== maxVerMatch[1]) {
      throw new Error(`major version of 'requires-python' min (${minVerMatch[0]}) and max (${maxVerMatch[0]}) don't agree`);
    }
    const minMajor = +minVerMatch[1];
    const minMinor = +minVerMatch[2];
    const maxMinor = +maxVerMatch[2];
    assert(maxMinor >= minMinor, "max version is not greater than or equal to min version");
    let minor = minMinor;
    const versions = [];
    while (minor <= maxMinor) {
      versions.push(`${minMajor}.${minor}`);
      minor++;
    }
    setOutput("versions", JSON.stringify(versions));
    setOutput("min_python", versions.at(0));
    setOutput("max_python", versions.at(-1));
  } catch (error) {
    setFailed(error.message);
  }
}

function setOutput(name, value) {
  console.log(`::set-output name=${name}::${value}`);
}

function setFailed(message) {
  console.log(`::error::${message}`);
  process.exit(1);
}

if (import.meta.filename === process.argv[1]) {
  parsePyproject();
}

export default parsePyproject;
