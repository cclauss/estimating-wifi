//nolint:typecheck
package tlp

import (
	"fmt"
	"io/ioutil"
	"os/exec"
	"strings"
	"syscall"

	"github.com/rs/zerolog/log"
	"gsa.gov/18f/internal/config"
	"gsa.gov/18f/internal/session-counter-helper/constants"
	"gsa.gov/18f/internal/session-counter-helper/state"
	"gsa.gov/18f/internal/wifi-hardware-search/models"
)

func TSharkRunner(adapter string) []string {
	tsharkCmd := exec.Command(
		config.GetWiresharkPath(),
		"-a", fmt.Sprintf("duration:%d", config.GetWiresharkDuration()),
		"-i", adapter,
		"-Tfields", "-e", "wlan.sa")

	tsharkOut, err := tsharkCmd.StdoutPipe()
	if err != nil {
		log.Error().
			Err(err).
			Msg("could not open wireshark pipe")
	}
	tsharkErr, err2 := tsharkCmd.StderrPipe()
	if err2 != nil {
		log.Error().
			Err(err2).
			Msg("could not open wireshark stderr pipe")
	}

	// The closer is called on exe exit. Idomatic use does not
	// explicitly call the closer. BUT DO WE HAVE LEAKS?
	defer tsharkOut.Close()
	defer tsharkErr.Close()

	err = tsharkCmd.Start()
	if err != nil {
		log.Error().
			Err(err).
			Msg("could not execute wireshark")
	}
	tsharkBytes, err := ioutil.ReadAll(tsharkOut)
	if err != nil {
		log.Error().
			Err(err).
			Msg("could not read from wireshark output")
	}
	tsharkErrBytes, err2 := ioutil.ReadAll(tsharkErr)
	if err2 != nil {
		log.Error().
			Err(err2).
			Msg("could not read from wireshark stderr")
	}

	//tsharkCmd.Wait()
	// From https://stackoverflow.com/questions/10385551/get-exit-code-go
	if err := tsharkCmd.Wait(); err != nil {
		if exiterr, ok := err.(*exec.ExitError); ok {
			// The program has exited with an exit code != 0
			if status, ok := exiterr.Sys().(syscall.WaitStatus); ok {
				log.Fatal().
					Int("exit status", status.ExitStatus()).
					Str("tshark command", tsharkCmd.String()).
					Str("stderr", string(tsharkErrBytes)).
					Str("stdout", string(tsharkBytes)).
					Msg("tshark exited unexpectedly")
			}
		} else {
			log.Fatal().
				Err(err).
				Msg("tshark did not wait")
		}
	}

	macs := strings.Split(string(tsharkBytes), "\n")

	return macs
}

type SharkFn func(string) []string
type MonitorFn func(*models.Device)
type SearchFn func() *models.Device

func SimpleShark(
	setMonitorFn MonitorFn,
	searchFn SearchFn,
	sharkFn SharkFn) bool {

	// Look up the adapter. Use the find-ralink library.
	// The % will trigger first time through, which we want.
	var dev *models.Device = nil
	// If the config doesn't have this in it, we get a divide by zero.
	dev = searchFn()

	// Only do a reading and continue the pipeline
	// if we find an adapter.
	if dev != nil && dev.Exists {
		// Load the config for use.
		// cfg.Wireshark.Adapter = dev.Logicalname
		setMonitorFn(dev)
		// This blocks for monitoring...
		macmap := sharkFn(dev.Logicalname)
		// Mark and remove too-short MAC addresses
		// for removal from the tshark findings.
		var keepers []string
		for _, mac := range macmap {
			if len(mac) >= constants.MACLENGTH {
				keepers = append(keepers, mac)
			}
		}
		StoreMacs(keepers)
	} else {
		log.Info().
			Msg("no wifi devices found; no scanning carried out")
		return false
	}
	return true
}

func StoreMacs(keepers []string) {
	// Do not log MAC addresses...
	for _, mac := range keepers {
		state.RecordMAC(mac)
	}
}
