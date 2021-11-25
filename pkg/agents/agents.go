package agents

import (
	"fmt"
	"runtime"

	test "github.com/bboymimi/easy-flamegraph/pkg/testpkg"
	"github.com/bboymimi/easy-flamegraph/pkg/workers"
)

func Start() {}

func Stop() {}

func Run() {
	nrCPU := runtime.NumCPU()

	// Create new threads pool
	pool := workers.NewPool(nrCPU)

	// Start the procutils capturing
	t := test.NewProcs(pool)
	t.Test()

	// Let the threads do the work
	pool.Start()

	if err := pool.Wait(); err != nil {
		fmt.Println(err)
	}
}
